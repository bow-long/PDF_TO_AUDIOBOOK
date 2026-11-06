from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pdf_audiobook.config import Config
from pdf_audiobook.pipeline import find_voice, run


# Edit these values, then run this file in VS Code. No command-line arguments
# are required.
INPUT_FOLDER = Path("file_input")
OUTPUT_FOLDER = Path("Output")
VOICES_FOLDER = Path("voices")
VOICE_NAME = ""  # Leave blank when voices contains exactly one .onnx model.
PIPER_EXECUTABLE = "piper"


class ProgressBars:
    def __init__(self) -> None:
        self.bars: dict[str, object] = {}
        self.current: dict[str, int] = {}

    def update(self, phase: str, current: int, total: int) -> None:
        import typer

        if phase not in self.bars:
            bar = typer.progressbar(length=total, label=self.label(phase))
            bar.__enter__()
            self.bars[phase] = bar
            self.current[phase] = 0
        bar = self.bars[phase]
        delta = current - self.current[phase]
        if delta > 0:
            bar.update(delta)
        self.current[phase] = current
        if current == total:
            bar.__exit__(None, None, None)

    @staticmethod
    def label(phase: str) -> str:
        return "Reading/OCR pages" if phase == "pages" else "Creating audio"

    def close(self) -> None:
        for phase, bar in self.bars.items():
            if self.current[phase] < getattr(bar, "length", 0):
                bar.__exit__(None, None, None)


def main() -> None:
    model = find_voice(VOICES_FOLDER, VOICE_NAME or None)
    print(f"Using voice: {model.stem}")
    progress = ProgressBars()
    try:
        report = run(
            INPUT_FOLDER,
            OUTPUT_FOLDER,
            Config(
                piper_model=str(model),
                piper_executable=PIPER_EXECUTABLE,
            ),
            progress=progress.update,
        )
    finally:
        progress.close()
    print(report)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
