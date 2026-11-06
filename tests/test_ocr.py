import cv2
import numpy as np

from pdf_audiobook.ocr import _indra


def test_indra_uses_current_image_api(monkeypatch):
    class Page:
        text = "recognized text"

    class Engine:
        def ocr(self, image):
            assert image.ndim == 2
            return Page()

    class Indra:
        @staticmethod
        def load():
            return Engine()

    monkeypatch.setitem(__import__("sys").modules, "indra_ocr", Indra)
    _, encoded = cv2.imencode(".png", np.zeros((4, 4), dtype=np.uint8))

    assert _indra(encoded.tobytes(), "eng") == "recognized text"
