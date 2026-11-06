from __future__ import annotations
import hashlib, json, os
from pathlib import Path
from typing import Any

def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)

def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(value, encoding="utf-8")
    os.replace(tmp, path)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""): h.update(block)
    return h.hexdigest()

def valid_checkpoint(path: Path, expected_sha: str | None = None) -> bool:
    return path.is_file() and (expected_sha is None or sha256(path) == expected_sha)

class RunState:
    def __init__(self, root: Path, fingerprint: str):
        self.root, self.path, self.fingerprint = root, root / "run.json", fingerprint
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {
            "version": 1, "config_fingerprint": fingerprint, "status": "running",
            "pages": {}, "segments": {}, "errors": []
        }
        if self.data.get("config_fingerprint") != fingerprint:
            raise ValueError("configuration fingerprint changed; use a new output directory")
    def save(self) -> None: atomic_json(self.path, self.data)
    def mark(self, group: str, key: str, value: Any) -> None:
        self.data.setdefault(group, {})[key] = value; self.save()
