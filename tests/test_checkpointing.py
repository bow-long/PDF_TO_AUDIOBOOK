from pdf_audiobook.checkpointing import atomic_json, valid_checkpoint
def test_atomic_checkpoint(tmp_path):
    p = tmp_path / "state.json"; atomic_json(p, {"ok": True})
    assert valid_checkpoint(p)

