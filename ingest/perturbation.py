from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

def load_perturbation(root: Path, entity_name: str) -> dict:
    p = root / "entities" / entity_name / "perturbation.json"
    if not p.exists():
        return {"enabled": False}
    return json.loads(p.read_text(encoding="utf-8"))

def apply_perturbation(entity_name: str, report: dict, mutation_receipt: dict, governance_receipt: dict):
    perturb = load_perturbation(Path("."), entity_name)
    if not perturb.get("enabled", False):
        return {
            "receipt_version": "1.0",
            "entity": entity_name,
            "perturbation_enabled": False,
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        }

    mode = perturb.get("mode", "set")
    target = perturb.get("target", "status")
    value = perturb.get("value", "denied")

    if target == "status":
        report["status"] = value
    elif target == "mutation_type":
        mutation_receipt["mutation_type"] = value
    elif target == "governance_authorized":
        governance_receipt["authorized"] = bool(value)

    return {
        "receipt_version": "1.0",
        "entity": entity_name,
        "perturbation_enabled": True,
        "mode": mode,
        "target": target,
        "value": value,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

def write_perturbation_receipt(reports_root: Path, receipt: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "perturbation_receipt.json").write_text(
        json.dumps(receipt, indent=2), encoding="utf-8"
    )