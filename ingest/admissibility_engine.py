from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

def load_admissibility_policy(path: Path) -> dict:
    if not path.exists():
        return {
            "policy_version": "1.0",
            "allowed_transitions": {
                "plan": ["artifact_ingestion", "configuration_change", "documentation_change", "policy_change", "unknown_mutation"],
                "install": ["artifact_ingestion", "configuration_change", "documentation_change"]
            },
            "blocked_sources_containing": [
                ".git/",
                ".gitmodules",
                ".gitconfig"
            ]
        }
    return json.loads(path.read_text(encoding="utf-8"))

def evaluate_admissibility(source: Path, mode: str, mutation_type: str, policy: dict) -> dict:
    checks_passed = []
    checks_failed = []

    allowed = policy.get("allowed_transitions", {}).get(mode, [])
    if mutation_type in allowed:
        checks_passed.append("transition_allowed")
    else:
        checks_failed.append("transition_not_allowed")

    source_str = str(source)
    blocked_markers = policy.get("blocked_sources_containing", [])
    if any(marker in source_str for marker in blocked_markers):
        checks_failed.append("source_blocked_by_admissibility")
    else:
        checks_passed.append("source_not_blocked")

    admissible = len(checks_failed) == 0

    transition_receipt = {
        "receipt_version": "1.0",
        "mode": mode,
        "mutation_type": mutation_type,
        "source": source_str,
        "admissible": admissible,
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

    admissibility_receipt = {
        "receipt_version": "1.0",
        "policy_version": policy.get("policy_version", "unknown"),
        "mode": mode,
        "mutation_type": mutation_type,
        "source": source_str,
        "admissible": admissible,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

    return transition_receipt, admissibility_receipt

def write_admissibility_reports(reports_root: Path, transition_receipt: dict, admissibility_receipt: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "transition_receipt.json").write_text(
        json.dumps(transition_receipt, indent=2), encoding="utf-8"
    )
    (reports_root / "admissibility_receipt.json").write_text(
        json.dumps(admissibility_receipt, indent=2), encoding="utf-8"
    )