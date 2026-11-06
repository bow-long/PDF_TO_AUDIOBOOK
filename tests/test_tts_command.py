from pdf_audiobook.tts import piper_command


def test_missing_piper_returns_no_command(monkeypatch):
    monkeypatch.setattr("pdf_audiobook.tts.shutil.which", lambda _: None)
    monkeypatch.setattr("pdf_audiobook.tts.importlib.util.find_spec", lambda _: None)

    assert piper_command("piper") is None


def test_python_piper_module_is_used_when_executable_is_missing(monkeypatch):
    monkeypatch.setattr("pdf_audiobook.tts.shutil.which", lambda _: None)
    monkeypatch.setattr(
        "pdf_audiobook.tts.importlib.util.find_spec",
        lambda _: object(),
    )

    command = piper_command("piper")

    assert command is not None
    assert command[1:] == ["-m", "piper"]
