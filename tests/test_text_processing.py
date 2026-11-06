from pdf_audiobook.text_processing import normalize, segment
def test_dehyphenate_and_segments():
    assert normalize("well-\nknown   text") == "wellknown text"
    assert [s.id for s in segment("One. Two. Three.", 8)] == ["000000", "000001", "000002"]

