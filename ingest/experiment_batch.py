from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

def build_experiment_manifest(mode: str, entity_names: list[str], trials: int, stress_test: bool, policy_surface: bool, phase_diagram: bool) -> dict:
    return {
        "manifest_version": "1.0",
        "mode": mode,
        "entity_names": entity_names,
        "trial_count": trials,
        "stress_test": bool(stress_test),
        "policy_surface": bool(policy_surface),
        "phase_diagram": bool(phase_diagram),
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

def write_experiment_manifest(reports_root: Path, manifest: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "experiment_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")