from __future__ import annotations
from pathlib import Path
import json
from .config import load_manifest_schema

def load_bundle_manifest(source_dir: Path):
    manifest_path = source_dir / "BUNDLE_MANIFEST.json"
    if not manifest_path.exists():
        return None
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    schema = load_manifest_schema()
    missing = [f for f in schema["required_fields"] if f not in data]
    if missing:
        raise ValueError(f"Bundle manifest missing required fields: {', '.join(missing)}")
    return data

def resolve_targets_from_manifest(manifest: dict | None):
    if not manifest:
        return None
    if manifest.get("target_repos"):
        return manifest["target_repos"]
    if manifest.get("target_set"):
        return {"target_set": manifest["target_set"]}
    return None
