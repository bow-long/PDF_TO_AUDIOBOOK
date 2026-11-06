# PDF to Audiobook

CPU-only, resumable PDF extraction/OCR to Piper TTS and WAV/MP3 assembly.

Install the pipeline and its PDF/OCR dependencies:

```powershell
python -m pip install -e ".[pdf,ocr,piper]"
```

Run the complete pipeline in one command:

```powershell
python -m pdf_audiobook -v en_US-lessac-medium
```

You can also run it without any command-line arguments. Edit the settings at
the top of [`pdf_audiobook/__main__.py`](./pdf_audiobook/__main__.py), then
press Run in VS Code or run:

```powershell
python pdf_audiobook\__main__.py
```

The script uses `file_input`, `output`, and `voices` by default. Set
`VOICE_NAME` to the voice filename or stem when the `voices` folder contains
more than one model.

TTS uses `workers` from [`config.py`](./pdf_audiobook/config.py) to generate
multiple segment buffers in parallel. Segment order is preserved when the
final audiobook is assembled. To combine existing buffers separately, edit
the settings in [`combine_audio.py`](./combine_audio.py) and run:

```powershell
python combine_audio.py
```

Put exactly one PDF in `file_input` and the Piper model plus its `.onnx.json`
metadata file in `voices`. The command discovers the selected voice, validates
it, reads/OCRs each PDF page, creates each audio buffer, and shows progress for
both phases while writing:

```text
output/
  pages/              extracted or OCR text, one file per PDF page
  segments/           individual WAV audio buffers
  audiobook.wav       combined final audiobook
  report.json         completion summary
```

Use the installed command instead if preferred:

```powershell
pdf-audiobook -v en_US-lessac-medium
```

In VS Code, prefer running `python -m pdf_audiobook ...` from the project root.
The module entry point also supports launching `pdf_audiobook\__main__.py`
directly.

An explicit PDF path is also supported:

```powershell
python -m pdf_audiobook process book.pdf -o output --piper-model voices/en_US-lessac-medium.onnx
```

If `voices` contains exactly one model, `-v` can be omitted:

```powershell
python -m pdf_audiobook
```

Use `--input`, `--output`, and `--voices` to override the default folders.

The pipeline uses the installed Piper Python module automatically. Indra OCR
is used automatically for pages without enough extractable text. If Piper is
not installed yet, run:

```powershell
python -m pip install piper-tts
```

Indra OCR 1.1.2 is an optional lazy integration (Python 3.10+, ONNX Runtime CPU); it may download models on first use. Disable it with `--no-use-indra` to use Tesseract (`pytesseract` plus the system Tesseract executable). Piper is invoked as an external executable with a local `.onnx` voice model; missing tools produce explicit errors. MP3 output additionally requires FFmpeg. Completed page and segment artifacts are retained under the output directory and are safe to resume.
