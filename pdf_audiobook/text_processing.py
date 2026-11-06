from __future__ import annotations
import re
from dataclasses import dataclass
def normalize(text: str) -> str:
    text = re.sub(r"-\s*\n\s*", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
@dataclass(frozen=True)
class Segment:
    id: str
    text: str
def segment(text: str, limit: int = 1800) -> list[Segment]:
    if limit < 1: raise ValueError("segment limit must be positive")
    sentences = re.split(r"(?<=[.!?])\s+", normalize(text))
    chunks, current = [], ""
    for sentence in sentences:
        if not sentence: continue
        if current and len(current) + len(sentence) + 1 > limit:
            chunks.append(current); current = ""
        current = (current + " " + sentence).strip()
    if current: chunks.append(current)
    return [Segment(f"{i:06d}", value) for i, value in enumerate(chunks)]

