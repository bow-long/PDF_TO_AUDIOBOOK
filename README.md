# PDF to Audiobook

This project converts a PDF file to an audiobook.

The program:

- Reads text from the PDF.
- Uses Indra OCR for pages with little or no text.
- Creates WAV audio segments with Piper TTS.
- Combines the segments into one audiobook.
- Saves progress so you can run the process again.

## Requirements

Install Python 3.10 or later.

Install the project and its dependencies:

```powershell
python -m pip install -e ".[pdf,ocr,piper]"
```

The `piper` extra installs Piper TTS.
The `ocr` extra installs Indra OCR.
The `pdf` extra installs PDF page rendering support.

## Folder setup

Create these folders in the project folder:

```text
PDF_TO_AUDIOBOOK\
  file_input\
  voices\
```

Put one PDF file in `file_input`.

Put the Piper voice files in `voices`:

```text
voices\
  en_US-amy-medium.onnx
  en_US-amy-medium.onnx.json
```

The `.onnx` file and the `.onnx.json` file must have the same base name.

## Run from VS Code

The recommended method does not use command-line arguments.

Open [pdf_audiobook/__main__.py](./pdf_audiobook/__main__.py).
Edit these settings when required:

```python
INPUT_FOLDER = Path("file_input")
OUTPUT_FOLDER = Path("Output")
VOICES_FOLDER = Path("voices")
VOICE_NAME = ""
```

Set `VOICE_NAME` to the voice file name or voice name.
For example:

```python
VOICE_NAME = "en_US-amy-medium"
```

Leave `VOICE_NAME` empty when `voices` contains one `.onnx` file.

Press **Run Python File** in VS Code.

You can also run the file from the project folder:

```powershell
python pdf_audiobook\__main__.py
```

The program checks the PDF and the voice before it starts processing.
It shows progress for page processing and audio creation.

## Output

The program creates the `Output` folder:

```text
Output\
  pages\       Text from each PDF page
  segments\    WAV audio files
  audiobook.wav
  report.json
```

The segment file names show their order.
The program uses this order when it creates `audiobook.wav`.

## Combine existing segments

Use [combine_audio.py](./combine_audio.py) to combine existing WAV segments.

Edit these settings in the file:

```python
SEGMENTS_FOLDER = Path("Output/segments")
FINAL_OUTPUT = Path("Output/audiobook.wav")
```

Run the script:

```powershell
python combine_audio.py
```

The script combines all `.wav` files in `SEGMENTS_FOLDER`.
It sorts the files by name before it combines them.

## Parallel processing

The program can create several audio segments at the same time.
The number of workers is set in
[pdf_audiobook/config.py](./pdf_audiobook/config.py).

For example:

```python
workers: int = 4
```

The final audiobook keeps the correct segment order.

## OCR

Indra OCR runs automatically when a PDF page has too little extractable text.
Indra may download its OCR models the first time that it runs.

To use Tesseract instead of Indra with the command-based interface, use:

```powershell
python -m pdf_audiobook process book.pdf -o Output `
  --piper-model voices\en_US-amy-medium.onnx `
  --no-use-indra
```

Tesseract requires the `pytesseract` Python package and the Tesseract
program installed on the computer.

## MP3 output

WAV output does not require FFmpeg.
MP3 output requires FFmpeg.

The command-based interface can create MP3 output:

```powershell
python -m pdf_audiobook process book.pdf -o Output `
  --piper-model voices\en_US-amy-medium.onnx `
  --output-format mp3
```

## Command-based interface

The package also provides a command-based interface.
Run it from the project folder:

```powershell
python -m pdf_audiobook
```

Use `-v` to select a voice:

```powershell
python -m pdf_audiobook -v en_US-amy-medium
```

Use `--input`, `--output`, and `--voices` to select different folders.

