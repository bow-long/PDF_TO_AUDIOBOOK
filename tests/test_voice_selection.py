import pytest

from pdf_audiobook.pipeline import find_voice


def test_find_voice_accepts_stem_and_requires_metadata(tmp_path):
    model = tmp_path / "reader.onnx"
    model.write_bytes(b"model")
    (tmp_path / "reader.onnx.json").write_text("{}", encoding="utf-8")

    assert find_voice(tmp_path, "reader") == model.resolve()


def test_find_voice_rejects_ambiguous_folder(tmp_path):
    for name in ("one", "two"):
        (tmp_path / f"{name}.onnx").write_bytes(b"model")
        (tmp_path / f"{name}.onnx.json").write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="multiple voices"):
        find_voice(tmp_path)


def test_find_voice_rejects_unknown_voice(tmp_path):
    (tmp_path / "reader.onnx").write_bytes(b"model")
    (tmp_path / "reader.onnx.json").write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="was not found"):
        find_voice(tmp_path, "missing")
