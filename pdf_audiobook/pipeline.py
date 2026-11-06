from __future__ import annotations
import json
import shutil
import concurrent.futures
from pathlib import Path
from collections.abc import Callable
from .audio import assemble
from .checkpointing import RunState, atomic_json, sha256
from .config import Config
from .ocr import extract_pages
from .text_processing import normalize, segment
from .tts import piper_command, synthesize


def find_voice(voices_dir: Path, voice: str | None = None) -> Path:
    voices_dir = voices_dir.expanduser().resolve()
    if not voices_dir.is_dir():
        raise ValueError(f"voices folder does not exist: {voices_dir}")
    models = sorted(item for item in voices_dir.glob("*.onnx") if item.is_file())
    if not models:
        raise ValueError(f"voices folder contains no .onnx models: {voices_dir}")
    if voice:
        requested = Path(voice).name
        matches = [
            item for item in models
            if item.name == requested or item.stem == requested
        ]
        if not matches:
            names = ", ".join(item.stem for item in models)
            raise ValueError(f"voice '{voice}' was not found; available voices: {names}")
        model = matches[0]
    elif len(models) == 1:
        model = models[0]
    else:
        names = ", ".join(item.stem for item in models)
        raise ValueError(f"multiple voices found; choose one with --voice: {names}")
    metadata = model.with_suffix(".onnx.json")
    if not metadata.is_file():
        raise ValueError(f"voice metadata file not found beside model: {metadata}")
    return model


def resolve_input(source: Path) -> Path:
    source = source.expanduser().resolve()
    if source.is_file():
        return source
    if source.is_dir():
        pdfs = sorted(
            item for item in source.iterdir()
            if item.is_file() and item.suffix.lower() == ".pdf"
        )
        if len(pdfs) == 1:
            return pdfs[0]
        if not pdfs:
            raise ValueError(f"input folder contains no PDF files: {source}")
        names = ", ".join(item.name for item in pdfs)
        raise ValueError(f"input folder must contain exactly one PDF; found: {names}")
    raise ValueError(f"input path does not exist: {source}")


def run(
    pdf: Path,
    output: Path,
    config: Config,
    progress: Callable[[str, int, int], None] | None = None,
) -> dict:
    pdf = resolve_input(pdf)
    output = output.resolve()
    if pdf.suffix.lower() != ".pdf":
        raise ValueError("input must be a PDF")
    config.validate()
    if not config.piper_model:
        raise ValueError("Piper model is required (--piper-model path.onnx)")
    model = Path(config.piper_model).expanduser()
    if not model.is_file():
        raise ValueError(f"Piper model file not found: {model}")
    if piper_command(config.piper_executable) is None:
        raise ValueError(
            "Piper is not installed. Run 'python -m pip install piper-tts' "
            "or provide a standalone piper executable."
        )
    if config.output_format == "mp3" and not (
        Path(config.encoder_executable).is_file() or shutil.which(config.encoder_executable)
    ):
        raise ValueError(f"FFmpeg executable not found: {config.encoder_executable}")
    output.mkdir(parents=True, exist_ok=True)
    state = RunState(output, config.fingerprint()); state.data.update({"input": str(pdf), "input_sha256": sha256(pdf)}); state.save()
    pages = extract_pages(
        pdf, output / "pages", config.dpi, config.ocr_language,
        config.min_text_chars, config.workers, config.use_indra,
        progress=lambda current, total: progress("pages", current, total) if progress else None,
    )
    text = normalize("\n".join(p.text for p in pages))
    atomic_json(output / "text.json", {"pages": len(pages), "characters": len(text)})
    segments = segment(text, config.max_segment_chars)
    wavs = [output / "segments" / f"{s.id}.wav" for s in segments]
    pending = [
        (s, path) for s, path in zip(segments, wavs)
        if not path.exists()
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.workers) as pool:
        futures = {
            pool.submit(synthesize, item.text, path, config): (item, path)
            for item, path in pending
        }
        completed = len(segments) - len(pending)
        if progress and completed:
            progress("audio", completed, len(segments))
        for future in concurrent.futures.as_completed(futures):
            item, path = futures[future]
            future.result()
            completed += 1
            state.mark("segments", item.id, {"path": str(path), "sha256": sha256(path)})
            if progress:
                progress("audio", completed, len(segments))
    for item, path in zip(segments, wavs):
        if path.exists() and item.id not in state.data.get("segments", {}):
            state.mark("segments", item.id, {"path": str(path), "sha256": sha256(path)})
    final = output / f"audiobook.{config.output_format}"; assemble(wavs, final, config)
    state.data["status"] = "complete"; state.data["output"] = str(final); state.save()
    report = {"status": "complete", "pages": len(pages), "segments": len(segments), "output": str(final)}
    atomic_json(output / "report.json", report); return report
