from __future__ import annotations
from pathlib import Path
import hashlib
import json

def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def replay_reports(reports_root: Path) -> dict:
    execution_receipt = _load_json(reports_root / "execution_receipt.json")
    state_hash = (reports_root / "state_hash.txt").read_text(encoding="utf-8").strip()
    artifact_hash = (reports_root / "artifact_hash.txt").read_text(encoding="utf-8").strip()

    report_material = {
        "mode": execution_receipt.get("mode"),
        "source": execution_receipt.get("source"),
        "status": "authorized" if execution_receipt.get("state_hash_after") else "unknown",
    }

    recomputed_state_before = _sha256_text(f"{execution_receipt.get('mode')}|before|{artifact_hash}")
    recomputed_state_after = _sha256_text(
        f"{execution_receipt.get('mode')}|after|{execution_receipt.get('report_hash')}"
    )

    checks_passed = []
    checks_failed = []

    if artifact_hash == execution_receipt.get("bundle_hash"):
        checks_passed.append("artifact_hash_matches_receipt")
    else:
        checks_failed.append("artifact_hash_mismatch")

    if recomputed_state_before == execution_receipt.get("state_hash_before"):
        checks_passed.append("state_hash_before_reproducible")
    else:
        checks_failed.append("state_hash_before_mismatch")

    if recomputed_state_after == execution_receipt.get("state_hash_after"):
        checks_passed.append("state_hash_after_reproducible")
    else:
        checks_failed.append("state_hash_after_mismatch")

    if state_hash == execution_receipt.get("state_hash_after"):
        checks_passed.append("stored_state_hash_matches_receipt")
    else:
        checks_failed.append("stored_state_hash_mismatch")

    result = {
        "replay_version": "1.0",
        "status": "PASS" if not checks_failed else "FAIL",
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "recomputed_state_hash_before": recomputed_state_before,
        "recomputed_state_hash_after": recomputed_state_after,
        "recorded_state_hash_after": execution_receipt.get("state_hash_after"),
    }
    return result

def write_replay_reports(reports_root: Path, result: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "replay_verification.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )

    lines = [
        "# Deterministic Replay Verification",
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
    (reports_root / "replay_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")