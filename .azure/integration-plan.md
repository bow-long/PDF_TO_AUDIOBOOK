# Integration hand-off
- Backend: `pdf_audiobook`; run `pdf-audiobook process <pdf> -o <run> --piper-model <model>`
- Health: CLI `--help`; build/test: `python -m pytest`
- Frontend: none (headless worker)
- API routes: none; CLI command `process`
- Database: none; filesystem checkpoints under the selected run directory; no seed data
- Services: pipeline-worker (essential), optional Blob adapter (enhancement, not implemented)
- External tools: optional Indra/Tesseract for OCR, Piper for TTS, FFmpeg for MP3
