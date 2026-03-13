from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

def write_runtime_manifest(reports_root: Path, mode: str, source: Path, entities: list[str], flags: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    payload = {
        "manifest_version": "1.0",
        "mode": mode,
        "source": str(source),
        "entities": entities,
        "flags": flags,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }
    (reports_root / "runtime_manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")