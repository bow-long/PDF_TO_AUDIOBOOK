from pathlib import Path
import json
import typer
from .config import Config
from .pipeline import find_voice, run

app = typer.Typer(help="Convert the PDF in file_input into an audiobook.")


class _ProgressBars:
    def __init__(self) -> None:
        self._bars: dict[str, object] = {}
        self._current: dict[str, int] = {}

    def update(self, phase: str, current: int, total: int) -> None:
        if phase not in self._bars:
            bar = typer.progressbar(length=total, label=self._label(phase))
            bar.__enter__()
            self._bars[phase] = bar
            self._current[phase] = 0
        bar = self._bars[phase]
        delta = current - self._current[phase]
        if delta > 0:
            bar.update(delta)
        self._current[phase] = current
        if current == total:
            bar.__exit__(None, None, None)

    @staticmethod
    def _label(phase: str) -> str:
        return "Reading/OCR pages" if phase == "pages" else "Creating audio"

    def close(self) -> None:
        for phase, bar in self._bars.items():
            if self._current[phase] < getattr(bar, "length", 0):
                bar.__exit__(None, None, None)


@app.callback()
def main(
    ctx: typer.Context,
    voice: str | None = typer.Option(None, "--voice", "-v", help="Voice filename or name from voices."),
    input_dir: Path = typer.Option(Path("file_input"), "--input", help="Folder containing one PDF."),
    output: Path = typer.Option(Path("output"), "--output", "-o"),
    voices_dir: Path = typer.Option(Path("voices"), "--voices", help="Folder containing Piper voices."),
    piper_executable: str = typer.Option("piper", "--piper-executable"),
) -> None:
    """Run the one-step pipeline when no subcommand is supplied."""
    if ctx.invoked_subcommand is not None:
        return
    try:
        model = find_voice(voices_dir, voice)
        typer.echo(f"Using voice: {model.stem}")
        bars = _ProgressBars()
        try:
            report = run(
                input_dir,
                output,
                Config(piper_model=str(model), piper_executable=piper_executable),
                progress=bars.update,
            )
        finally:
            bars.close()
        typer.echo(json.dumps(report, indent=2))
    except Exception as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(2)

@app.command()
def process(pdf: Path = typer.Argument(Path("file_input")),
            output: Path = typer.Option(..., "--output", "-o"),
            language: str = "eng", dpi: int = 200, workers: int = 1,
            piper_model: Path | None = typer.Option(None, "--piper-model"),
            piper_executable: str = "piper", output_format: str = "wav",
            use_indra: bool = True):
    """Process one PDF from PDF or file_input, resuming checkpoints in OUTPUT."""
    try:
        report = run(pdf, output, Config(ocr_language=language, dpi=dpi, workers=workers,
                                         piper_model=str(piper_model) if piper_model else None,
                                         piper_executable=piper_executable, output_format=output_format,
                                         use_indra=use_indra))
        typer.echo(json.dumps(report, indent=2))
    except Exception as exc:
        typer.echo(f"ERROR: {exc}", err=True); raise typer.Exit(2)
if __name__ == "__main__": app()
