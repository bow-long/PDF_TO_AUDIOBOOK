**Status**: Approved
**Created**: 2026-11-05
**Mode**: CPU-only local batch pipeline

## 1. Project Summary

Build a reproducible, CPU-only audiobook production pipeline for PDF books. The worker accepts born-digital or scanned PDFs, extracts text where possible, applies local OCR to scanned pages, normalizes and segments the resulting text, synthesizes speech with Piper, and assembles chapter-aware audiobook files. The first release is a scriptable local worker with no hosted API or user accounts.

## 2. Goals & Non-Goals

**Goals**:
- Process PDFs deterministically on machines without a GPU.
- Support text extraction with OCR fallback, configurable OCR language and resolution, and page-level resume.
- Produce inspectable OCR text, manifests, logs, and chapter-aware WAV/MP3 output.
- Keep Piper voice/model selection and audio encoding configurable.
- Fail safely per page/chapter and provide actionable progress and error reports.

**Non-Goals**:
- Cloud GPU inference, online OCR, or external TTS services.
- Multi-user accounts, a web dashboard, or a public API.
- Training or fine-tuning OCR/TTS models.

## 3. User Experience & Workflows

1. User invokes a CLI with an input PDF, output directory, OCR settings, Piper voice, and output format.
2. The worker fingerprints the input and creates a run manifest.
3. Each page is extracted directly when usable; otherwise it is rasterized and passed to local Tesseract OCR.
4. Text is cleaned, dehyphenated, joined across page boundaries, and split into chapter/section-sized speech segments.
5. Piper synthesizes each segment using CPU execution; segment audio and metadata are checkpointed.
6. The worker concatenates segments, writes chapter files plus a complete audiobook, and emits a report.
7. Re-running the same command resumes completed pages and segments unless the configuration fingerprint changes.

## 4. Architecture

The solution is a Python worker package exposed through a Typer CLI. Modules are separated into `pdf_input`, `ocr`, `text_processing`, `tts`, `audio`, `checkpointing`, and `reporting`. Temporary artifacts are written beneath a run directory and final artifacts are promoted only after validation. External executables (Tesseract, Piper, and an audio encoder) are invoked through controlled subprocess wrappers with timeouts, captured stderr, and version checks.

The default execution path is local filesystem storage for working data, with an optional Blob Storage adapter for source PDFs and generated audiobook artifacts. No network call is required for processing; models and binaries are installed or supplied locally.

## 5. Services & Data

**Services**:
- `pipeline-worker` (Python): batch orchestration, PDF extraction, OCR fallback, text normalization, Piper invocation, audio assembly, checkpointing, and reporting.

**Data Stores**:
- Blob Storage (optional deployment adapter): source PDFs, OCR text, manifests, and generated audio files.
- Local filesystem: required working directory and default mode for CPU-only runs.
- No relational database: run state is represented by versioned manifests and checkpoint files.

**Key artifacts**:
- `run.json`: input/config/model fingerprints and status.
- `pages/<number>.txt`: extracted or OCR text.
- `segments/<id>.wav`: checkpointed Piper output.
- `chapters/*.wav` and `audiobook.mp3`: final outputs.
- `report.json` and `report.txt`: timings, warnings, failures, and provenance.

## 6. Design System & UI

**Component Library**: None — headless CLI worker; no graphical UI is planned.
**Interaction model**: Typer commands with `--help`, structured progress, quiet mode, and JSON report output.
**Accessibility**: CLI output uses readable status labels, stable exit codes, and machine-readable diagnostics.

## 7. Security, Reliability & Operations

- Treat PDFs and OCR text as untrusted input; avoid shell interpolation and write only inside the selected run root.
- Validate file paths, size limits, executable paths, model files, and output extensions before processing.
- Do not log document contents by default; redact secrets and provide opt-in diagnostic excerpts.
- Use atomic writes, checksums, bounded subprocesses, and resumable checkpoints.
- Pin Python dependencies and record Tesseract/Piper/encoder versions in each report.
- Provide clear exit codes for invalid input, missing tools, partial processing, and successful completion.

## 8. Implementation Plan

1. Create the Python package, Typer CLI, configuration model, logging, and run-directory layout.
2. Implement PDF text extraction and page rasterization with configurable DPI.
3. Add Tesseract OCR fallback, language validation, normalization, dehyphenation, and page-level checkpoints.
4. Add chapter detection/configuration, deterministic segmentation, and text provenance metadata.
5. Integrate Piper through a safe subprocess adapter with voice/model validation and CPU settings.
6. Implement WAV concatenation, loudness/format validation, optional MP3 encoding, and chapter manifests.
7. Add local filesystem operation plus an isolated optional Blob Storage adapter.
8. Add unit tests for parsing, checkpoint recovery, path safety, segmentation, and subprocess failures; add fixture-based end-to-end tests with a small PDF.
9. Document installation of CPU dependencies, model provisioning, CLI examples, performance tuning, and troubleshooting.

## 9. Validation & Acceptance Criteria

- A text PDF and a scanned PDF complete successfully on a CPU-only machine.
- OCR fallback is selected only when extracted text is absent or below the configured quality threshold.
- Interrupted runs resume without repeating completed page OCR or TTS segments.
- The final audiobook, chapter files, manifest, and report have consistent durations and checksums.
- Missing Tesseract, Piper, voice model, or encoder produces a clear actionable error before partial work begins.
- Tests cover malformed PDFs, unsupported languages, hostile paths, subprocess timeouts, and partial page failures.
- A documented benchmark records throughput and peak memory for representative page counts.
