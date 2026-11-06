from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from pdf_audiobook.audio import assemble
from pdf_audiobook.config import Config


# Edit these values, then run this file in VS Code.
SEGMENTS_FOLDER = Path("Output/segments")
FINAL_OUTPUT = Path("Output/audiobook.wav")
FFMPEG_EXECUTABLE = "ffmpeg"


def main() -> None:
    wavs = sorted(SEGMENTS_FOLDER.glob("*.wav"))
    if not wavs:
        raise ValueError(f"no WAV segments found in {SEGMENTS_FOLDER.resolve()}")
    output_format = FINAL_OUTPUT.suffix.lower().lstrip(".")
    if output_format not in {"wav", "mp3"}:
        raise ValueError("FINAL_OUTPUT must end in .wav or .mp3")
    assemble(
        wavs,
        FINAL_OUTPUT,
        Config(output_format=output_format, encoder_executable=FFMPEG_EXECUTABLE),
    )
    print(f"Combined {len(wavs)} segments into {FINAL_OUTPUT}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
