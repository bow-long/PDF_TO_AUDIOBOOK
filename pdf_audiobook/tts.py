from __future__ import annotations
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path
from .config import Config
class TtsError(RuntimeError): pass


def piper_command(executable: str) -> list[str] | None:
    if shutil.which(executable) or Path(executable).is_file():
        return [executable]
    if executable != "piper":
        return None
    if importlib.util.find_spec("piper") is not None:
        return [sys.executable, "-m", "piper"]
    return None


def synthesize(text: str, output: Path, config: Config) -> None:
    if not config.piper_model: raise TtsError("Piper model is required (--piper-model path.onnx)")
    command = piper_command(config.piper_executable)
    if command is None:
        raise TtsError(
            "Piper is not installed. Run 'python -m pip install piper-tts' "
            "or provide a standalone piper executable."
        )
    arguments = (
        ["-m", config.piper_model, "-f", str(output)]
        if command[1:] == ["-m", "piper"]
        else ["--model", config.piper_model, "--output_file", str(output)]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([*command, *arguments],
                       input=text, text=True, capture_output=True, timeout=config.timeout_seconds, check=True)
    except FileNotFoundError as exc: raise TtsError(f"Piper executable not found: {config.piper_executable}") from exc
    except subprocess.TimeoutExpired as exc: raise TtsError("Piper timed out") from exc
    except subprocess.CalledProcessError as exc: raise TtsError(exc.stderr.strip() or "Piper failed") from exc
    if not output.is_file() or output.stat().st_size == 0:
        raise TtsError("Piper completed without producing an audio file")
