from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

def load_recovery(root: Path, entity_name: str) -> dict:
    p = root / "entities" / entity_name / "recovery.json"
    if not p.exists():
        return {"enabled": False}
    return json.loads(p.read_text(encoding="utf-8"))

def apply_recovery(root: Path, entity_name: str) -> dict:
    recovery = load_recovery(root, entity_name)
    perturb_path = root / "entities" / entity_name / "perturbation.json"

    receipt = {
        "receipt_version": "1.0",
        "entity": entity_name,
        "recovery_enabled": bool(recovery.get("enabled", False)),
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

    if recovery.get("enabled", False):
        if perturb_path.exists():
            perturb_path.write_text('{"enabled": false}\n', encoding="utf-8")
            receipt["recovered"] = True
            receipt["action"] = "disabled_perturbation"
        else:
            receipt["recovered"] = False
            receipt["action"] = "no_perturbation_file"
    else:
        receipt["recovered"] = False
        receipt["action"] = "recovery_not_enabled"

    return receipt

def write_recovery_receipt(reports_root: Path, receipt: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "recovery_receipt.json").write_text(
        json.dumps(receipt, indent=2), encoding="utf-8"
    )