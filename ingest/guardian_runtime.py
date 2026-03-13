from __future__ import annotations
from pathlib import Path
from datetime import datetime
import hashlib
import json

def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def load_guardian_policy(path: Path) -> dict:
    if not path.exists():
        return {
            "policy_version": "1.0",
            "execution_modes_touching_reality": ["install"],
            "high_sensitivity_roots": ["incoming", "entities", "configs"],
            "blocked_suffixes": [".exe", ".dll", ".so"],
            "boundary_actions": {
                "plan": "observe_only",
                "install": "mutation_boundary"
            }
        }
    return json.loads(path.read_text(encoding="utf-8"))

def evaluate_guardian_boundary(source: Path, mode: str, policy: dict) -> dict:
    source_str = str(source)
    touches_reality = mode in policy.get("execution_modes_touching_reality", [])
    high_sensitivity = any(root in source_str for root in policy.get("high_sensitivity_roots", []))
    blocked_suffix = source.is_file() and source.suffix.lower() in set(policy.get("blocked_suffixes", []))
    boundary_action = policy.get("boundary_actions", {}).get(mode, "unknown")

    verdict = "allow"
    reasons = []
    if blocked_suffix:
        verdict = "deny"
        reasons.append("blocked_suffix")
    elif touches_reality and high_sensitivity:
        verdict = "guarded_allow"
        reasons.append("touches_reality_high_sensitivity")
    elif touches_reality:
        verdict = "guarded_allow"
        reasons.append("touches_reality")
    else:
        reasons.append("observe_only")

    receipt = {
        "receipt_version": "1.0",
        "policy_version": policy.get("policy_version", "unknown"),
        "mode": mode,
        "source": source_str,
        "touches_reality": touches_reality,
        "high_sensitivity": high_sensitivity,
        "boundary_action": boundary_action,
        "verdict": verdict,
        "reasons": reasons,
        "guardian_hash": _sha256_text(json.dumps({
            "mode": mode,
            "source": source_str,
            "touches_reality": touches_reality,
            "high_sensitivity": high_sensitivity,
            "boundary_action": boundary_action,
            "verdict": verdict,
            "reasons": reasons,
        }, sort_keys=True)),
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }
    return receipt

def write_guardian_reports(reports_root: Path, receipt: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "guardian_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    (reports_root / "guardian_hash.txt").write_text(receipt["guardian_hash"] + "\n", encoding="utf-8")