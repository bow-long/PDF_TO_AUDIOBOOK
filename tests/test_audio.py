import wave

from pdf_audiobook.audio import assemble
from pdf_audiobook.config import Config


def _write_wav(path, frames):
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(22050)
        audio.writeframes(b"\0\0" * frames)


def test_assemble_allows_different_segment_lengths(tmp_path):
    first = tmp_path / "000000.wav"
    second = tmp_path / "000001.wav"
    output = tmp_path / "audiobook.wav"
    _write_wav(first, 10)
    _write_wav(second, 20)

    assemble([first, second], output, Config())

    with wave.open(str(output), "rb") as audio:
        assert audio.getnframes() == 30
