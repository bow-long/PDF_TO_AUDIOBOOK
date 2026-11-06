from pathlib import Path

import combine_audio


def test_combine_audio_defaults_to_segment_folder():
    assert combine_audio.SEGMENTS_FOLDER == Path("Output/segments")
    assert combine_audio.FINAL_OUTPUT.suffix == ".wav"
