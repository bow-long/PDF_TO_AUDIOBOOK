from __future__ import annotations
import concurrent.futures
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Callable
from .pdf_input import page_texts, render_page
from .checkpointing import atomic_text

class OcrUnavailable(RuntimeError): pass
class OcrError(RuntimeError): pass

def _tesseract(image: bytes, language: str) -> str:
    try:
        import pytesseract
        from PIL import Image
        import io
        return pytesseract.image_to_string(Image.open(io.BytesIO(image)), lang=language)
    except ImportError as exc:
        raise OcrUnavailable("install .[ocr] and Tesseract executable for OCR") from exc
    except Exception as exc: raise OcrError(str(exc)) from exc

def _indra(image: bytes, language: str) -> str:
    try:
        import indra_ocr
        import cv2
        import numpy as np

        engine = indra_ocr.load()
        gray = cv2.imdecode(np.frombuffer(image, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            raise OcrError("Indra could not decode the rendered page image")
        page = engine.ocr(gray)
        return page.text
    except ImportError as exc:
        raise OcrUnavailable("install indra-ocr>=1.1.2 (Python 3.10+) or disable Indra") from exc
    except Exception as exc: raise OcrError(f"Indra OCR failed: {exc}") from exc

def _process_page(item: tuple[int, str, Path, int, str, int, bool]) -> "PageResult":
    n, text, pdf, dpi, language, threshold, use_indra = item
    if len(text.strip()) >= threshold:
        return PageResult(n, text, "pdf")
    image = render_page(pdf, n, dpi)
    value = _indra(image, language) if use_indra else _tesseract(image, language)
    return PageResult(n, value, "indra" if use_indra else "tesseract")

@dataclass
class PageResult:
    number: int
    text: str
    source: str

def extract_pages(pdf: Path, out: Path, dpi: int, language: str, threshold: int,
                  workers: int = 1, use_indra: bool = True,
                  progress: Callable[[int, int], None] | None = None) -> list[PageResult]:
    direct = list(page_texts(pdf)); out.mkdir(parents=True, exist_ok=True)
    if progress:
        progress(0, len(direct))
    pending = []
    results = []
    for n, text in direct:
        checkpoint = out / f"{n:06d}.txt"
        if checkpoint.is_file():
            results.append(PageResult(n, checkpoint.read_text(encoding="utf-8"), "checkpoint"))
            if progress:
                progress(len(results), len(direct))
        else:
            pending.append((n, text, pdf, dpi, language, threshold, use_indra))

    def persist(result: PageResult) -> None:
        atomic_text(out / f"{result.number:06d}.txt", result.text)
        results.append(result)
        if progress:
            progress(len(results), len(direct))

    if workers == 1:
        for item in pending:
            persist(_process_page(item))
    else:
        # map preserves input order, making output and failures deterministic.
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
            for result in pool.map(_process_page, pending):
                persist(result)
    return sorted(results, key=lambda x: x.number)
