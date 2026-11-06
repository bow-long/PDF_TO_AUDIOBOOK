import pytest

from pdf_audiobook.pipeline import resolve_input


def test_resolve_input_finds_single_pdf(tmp_path):
    pdf = tmp_path / "book.PDF"
    pdf.write_bytes(b"%PDF")

    assert resolve_input(tmp_path) == pdf.resolve()


def test_resolve_input_rejects_multiple_pdfs(tmp_path):
    (tmp_path / "one.pdf").write_bytes(b"%PDF")
    (tmp_path / "two.pdf").write_bytes(b"%PDF")

    with pytest.raises(ValueError, match="exactly one PDF"):
        resolve_input(tmp_path)


def test_resolve_input_rejects_empty_folder(tmp_path):
    with pytest.raises(ValueError, match="no PDF files"):
        resolve_input(tmp_path)
