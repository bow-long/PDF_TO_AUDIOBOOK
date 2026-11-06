from __future__ import annotations
from pathlib import Path
from typing import Iterator

class PdfError(RuntimeError): pass

def page_texts(pdf: Path) -> Iterator[tuple[int, str]]:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf))
        for i, page in enumerate(reader.pages):
            yield i, page.extract_text() or ""
    except Exception as exc:
        raise PdfError(f"unable to read PDF {pdf}: {exc}") from exc

def render_page(pdf: Path, number: int, dpi: int):
    try:
        import fitz
        with fitz.open(str(pdf)) as doc:
            page = doc.load_page(number)
            pix = page.get_pixmap(dpi=dpi, alpha=False)
            return pix.tobytes("png")
    except ImportError as exc:
        raise PdfError("scanned PDFs require optional dependency pymupdf (pip install .[pdf])") from exc
    except Exception as exc:
        raise PdfError(f"cannot render page {number + 1}: {exc}") from exc
