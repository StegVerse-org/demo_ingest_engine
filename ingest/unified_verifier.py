from __future__ import annotations
from pathlib import Path
import json

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def verify_unified_provenance(root: Path) -> dict:
    reports_root = root / "reports"
    state_hash_path = reports_root / "state_hash.txt"
    event_receipt_path = reports_root / "event_ledger_receipt.json"
    prov_path = reports_root / "provenance_receipt.json"

    checks_passed = []
    checks_failed = []

    state_hash = state_hash_path.read_text(encoding="utf-8").strip() if state_hash_path.exists() else None
    event_hash = _load_json(event_receipt_path).get("batch_hash") if event_receipt_path.exists() else None
    prov = _load_json(prov_path) if prov_path.exists() else None

    if state_hash and prov and prov.get("state_hash") == state_hash:
        checks_passed.append("state_hash_linked")
    else:
        checks_failed.append("state_hash_link_broken")

    if event_hash and prov and prov.get("event_batch_hash") == event_hash:
        checks_passed.append("event_batch_hash_linked")
    else:
        checks_failed.append("event_batch_hash_link_broken")

    if prov and prov.get("provenance_hash"):
        checks_passed.append("provenance_hash_present")
    else:
        checks_failed.append("provenance_hash_missing")

    return {
        "unified_verification_version": "1.0",
        "status": "PASS" if not checks_failed else "FAIL",
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
    }

def write_unified_verification_reports(reports_root: Path, result: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "unified_provenance_verification.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    lines = [
        "# Unified Provenance Verification",
        "",
        f"- Status: **{result['status']}**",
        f"- Checks passed: `{len(result['checks_passed'])}`",
        f"- Checks failed: `{len(result['checks_failed'])}`",
    ]
    (reports_root / "unified_provenance_verification.md").write_text("\n".join(lines) + "\n", encoding="utf-8")