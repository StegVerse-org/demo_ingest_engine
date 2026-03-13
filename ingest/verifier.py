from __future__ import annotations
from pathlib import Path
import hashlib
import json

def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def verify_reports(reports_root: Path) -> dict:
    checks_passed = []
    checks_failed = []

    exec_path = reports_root / "execution_receipt.json"
    gov_path = reports_root / "governance_receipt.json"
    mut_path = reports_root / "mutation_receipt.json"
    state_hash_path = reports_root / "state_hash.txt"
    artifact_hash_path = reports_root / "artifact_hash.txt"
    state_dir = reports_root / "state_graph"

    execution_receipt = _load_json(exec_path) if exec_path.exists() else None
    governance_receipt = _load_json(gov_path) if gov_path.exists() else None
    mutation_receipt = _load_json(mut_path) if mut_path.exists() else None

    if execution_receipt:
        checks_passed.append("execution_receipt_exists")
    else:
        checks_failed.append("execution_receipt_missing")

    if governance_receipt:
        checks_passed.append("governance_receipt_exists")
    else:
        checks_failed.append("governance_receipt_missing")

    if mutation_receipt:
        checks_passed.append("mutation_receipt_exists")
    else:
        checks_failed.append("mutation_receipt_missing")

    if execution_receipt:
        expected_state_after = execution_receipt.get("state_hash_after")
        if state_hash_path.exists():
            actual_state_after = state_hash_path.read_text(encoding="utf-8").strip()
            if actual_state_after == expected_state_after:
                checks_passed.append("state_hash_matches_execution_receipt")
            else:
                checks_failed.append("state_hash_mismatch")
        else:
            checks_failed.append("state_hash_missing")

        if artifact_hash_path.exists():
            actual_artifact_hash = artifact_hash_path.read_text(encoding="utf-8").strip()
            if actual_artifact_hash == execution_receipt.get("bundle_hash"):
                checks_passed.append("artifact_hash_matches_execution_receipt")
            else:
                checks_failed.append("artifact_hash_mismatch")
        else:
            checks_failed.append("artifact_hash_missing")

    if governance_receipt:
        if governance_receipt.get("policy_hash"):
            checks_passed.append("governance_policy_hash_present")
        else:
            checks_failed.append("governance_policy_hash_missing")

    if mutation_receipt and governance_receipt:
        if governance_receipt.get("mutation_type") == mutation_receipt.get("mutation_type"):
            checks_passed.append("mutation_type_consistent")
        else:
            checks_failed.append("mutation_type_inconsistent")

    if state_dir.exists():
        state_files = sorted(state_dir.glob("state_*.json"))
        if state_files:
            prev_id = None
            prev_hash = None
            chain_ok = True
            for sf in state_files:
                data = _load_json(sf)
                if prev_id is None:
                    if data.get("previous_state_id") is not None:
                        chain_ok = False
                else:
                    if data.get("previous_state_id") != prev_id:
                        chain_ok = False
                    if data.get("previous_state_hash") != prev_hash:
                        chain_ok = False
                prev_id = data.get("state_id")
                prev_hash = data.get("state_hash")
            if chain_ok:
                checks_passed.append("state_chain_continuity")
            else:
                checks_failed.append("state_chain_broken")
        else:
            checks_failed.append("state_chain_missing")
    else:
        checks_failed.append("state_graph_missing")

    return {
        "verification_version": "1.0",
        "status": "PASS" if not checks_failed else "FAIL",
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
    }

def write_verification_reports(reports_root: Path, result: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "verification_report.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )

    lines = [
        "# Verification Summary",
        "",
        f"- Status: **{result['status']}**",
        f"- Checks passed: `{len(result['checks_passed'])}`",
        f"- Checks failed: `{len(result['checks_failed'])}`",
        "",
        "## Passed",
        "",
    ]
    for item in result["checks_passed"]:
        lines.append(f"- {item}")
    lines += ["", "## Failed", ""]
    for item in result["checks_failed"]:
        lines.append(f"- {item}")
    (reports_root / "verification_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")