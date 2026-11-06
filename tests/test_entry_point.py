from pathlib import Path


def test_module_entry_point_supports_direct_script_import():
    source = Path("pdf_audiobook/__main__.py").read_text(encoding="utf-8")

    assert "from pdf_audiobook.config import Config" in source
    assert "from pdf_audiobook.pipeline import find_voice, run" in source
