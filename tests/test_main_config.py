from pathlib import Path

import pdf_audiobook.__main__ as main_module


def test_main_has_editable_folder_configuration():
    assert isinstance(main_module.INPUT_FOLDER, Path)
    assert isinstance(main_module.OUTPUT_FOLDER, Path)
    assert isinstance(main_module.VOICES_FOLDER, Path)
    assert isinstance(main_module.VOICE_NAME, str)
