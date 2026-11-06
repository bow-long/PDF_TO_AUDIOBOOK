from __future__ import annotations
import hashlib, json
from dataclasses import asdict, dataclass
from pathlib import Path

@dataclass(frozen=True)
class Config:
    ocr_language: str = "eng"
    dpi: int = 200
    workers: int = 4
    min_text_chars: int = 40
    max_segment_chars: int = 1800
    piper_executable: str = "piper"
    piper_model: str | None = None
    encoder_executable: str = "ffmpeg"
    output_format: str = "wav"
    timeout_seconds: int = 300
    use_indra: bool = True

    def fingerprint(self) -> str:
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()

    def validate(self) -> None:
        if self.dpi < 72 or self.dpi > 600: raise ValueError("dpi must be between 72 and 600")
        if self.workers < 1: raise ValueError("workers must be positive")
        if self.min_text_chars < 0: raise ValueError("min_text_chars must not be negative")
        if self.max_segment_chars < 1: raise ValueError("max_segment_chars must be positive")
        if self.timeout_seconds < 1: raise ValueError("timeout_seconds must be positive")
        if self.output_format not in {"wav", "mp3"}: raise ValueError("output_format must be wav or mp3")
        if self.output_format == "mp3" and not self.encoder_executable: raise ValueError("ffmpeg is required for mp3")
