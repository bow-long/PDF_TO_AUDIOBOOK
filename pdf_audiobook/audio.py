from __future__ import annotations
import subprocess, wave
from pathlib import Path
from .config import Config
class AudioError(RuntimeError): pass
def assemble(wavs: list[Path], output: Path, config: Config) -> None:
    if not wavs: raise AudioError("no audio segments")
    output.parent.mkdir(parents=True, exist_ok=True)
    if config.output_format == "wav":
        with wave.open(str(output), "wb") as target:
            params = None
            for item in wavs:
                with wave.open(str(item), "rb") as src:
                    current = src.getparams()
                    if params is None:
                        params = current
                        target.setparams(params)
                    elif current[:3] != params[:3]:
                        raise AudioError("audio segments have incompatible WAV formats")
                    target.writeframes(src.readframes(src.getnframes()))
    else:
        concat = output.with_suffix(".concat.txt")
        concat.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in wavs), encoding="utf-8")
        try: subprocess.run([config.encoder_executable, "-y", "-f", "concat", "-safe", "0", "-i", str(concat), str(output)],
                            capture_output=True, text=True, timeout=config.timeout_seconds, check=True)
        except FileNotFoundError as exc: raise AudioError("FFmpeg executable not found") from exc
        except subprocess.CalledProcessError as exc: raise AudioError(exc.stderr.strip() or "FFmpeg failed") from exc
