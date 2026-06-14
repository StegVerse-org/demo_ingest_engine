from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERIFICATION_VERSION = "1.0"
DEFAULT_HANDOFF_DIR = Path("cge_handoff")
DEFAULT_LEDGER_DIR = Path("event_ledger")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_handoff(handoff_dir: Path, ledger_dir: Path) -> dict[str, Any]:
    checks_passed: list[str] = []
    checks_failed: list[str] = []

    handoff_path = handoff_dir / "sandbox_receipt_handoff.json"
    handoff_md_path = handoff_dir / "sandbox_receipt_handoff.md"
    latest_batch_path = ledger_dir / "latest_sandbox_receipt_batch.json"
    ledger_verification_path = ledger_dir / "sandbox_receipt_ledger_verification.json"

    if handoff_path.exists():
        checks_passed.append("handoff_json_exists")
        handoff = _load_json(handoff_path)
    else:
        checks_failed.append("handoff_json_missing")
        handoff = {}

    if handoff_md_path.exists():
        checks_passed.append("handoff_markdown_exists")
    else:
        checks_failed.append("handoff_markdown_missing")

    if latest_batch_path.exists():
        checks_passed.append("latest_batch_exists")
        latest_batch = _load_json(latest_batch_path)
    else:
        checks_failed.append("latest_batch_missing")
        latest_batch = {}

    if ledger_verification_path.exists():
        checks_passed.append("ledger_verification_exists")
        ledger_verification = _load_json(ledger_verification_path)
    else:
        checks_failed.append("ledger_verification_missing")
        ledger_verification = {}

    if handoff.get("source_sha256") == _sha256_file(latest_batch_path) if latest_batch_path.exists() else False:
        checks_passed.append("source_hash_matches_latest_batch")
    else:
        checks_failed.append("source_hash_mismatch_latest_batch")

    if handoff.get("ledger_verification_sha256") == _sha256_file(ledger_verification_path) if ledger_verification_path.exists() else False:
        checks_passed.append("ledger_verification_hash_matches")
    else:
        checks_failed.append("ledger_verification_hash_mismatch")

    if ledger_verification.get("status") == "PASS":
        checks_passed.append("ledger_verification_status_pass")
    else:
        checks_failed.append(f"ledger_verification_status_not_pass:{ledger_verification.get('status')}")

    if handoff.get("ledger_verification", {}).get("status") == "PASS":
        checks_passed.append("handoff_embedded_ledger_status_pass")
    else:
        checks_failed.append("handoff_embedded_ledger_status_not_pass")

    allowed_verdicts = {"OBSERVE_ONLY", "READY_FOR_REVIEW", "BLOCKED_EXECUTION"}
    if handoff.get("verdict") in allowed_verdicts:
        checks_passed.append("verdict_is_known_classification")
    else:
        checks_failed.append(f"unknown_verdict:{handoff.get('verdict')}")

    if handoff.get("execution_authority") is False:
        checks_passed.append("execution_authority_false")
    else:
        checks_failed.append(f"execution_authority_not_false:{handoff.get('execution_authority')}")

    if handoff.get("install_authority") is False:
        checks_passed.append("install_authority_false")
    else:
        checks_failed.append(f"install_authority_not_false:{handoff.get('install_authority')}")

    if handoff.get("handoff_scope") == "classification_only":
        checks_passed.append("handoff_scope_classification_only")
    else:
        checks_failed.append(f"handoff_scope_invalid:{handoff.get('handoff_scope')}")

    constraints = set(handoff.get("constraints", [])) if isinstance(handoff.get("constraints"), list) else set()
    required_constraints = {
        "observe_only_handoff",
        "no_execution_authority",
        "no_install_authority",
        "cge_must_revalidate_before_action",
    }
    missing_constraints = sorted(required_constraints - constraints)
    if not missing_constraints:
        checks_passed.append("required_constraints_present")
    else:
        checks_failed.append(f"required_constraints_missing:{','.join(missing_constraints)}")

    latest_batch_summary = handoff.get("latest_batch", {}) if isinstance(handoff.get("latest_batch"), dict) else {}
    if latest_batch_summary.get("batch_sha256") == latest_batch.get("batch_sha256"):
        checks_passed.append("handoff_latest_batch_hash_matches")
    else:
        checks_failed.append("handoff_latest_batch_hash_mismatch")

    return {
        "sandbox_receipt_cge_handoff_verification_version": VERIFICATION_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "handoff_dir": str(handoff_dir),
        "ledger_dir": str(ledger_dir),
        "status": "PASS" if not checks_failed else "FAIL",
        "verdict": handoff.get("verdict"),
        "execution_authority": handoff.get("execution_authority"),
        "install_authority": handoff.get("install_authority"),
        "handoff_scope": handoff.get("handoff_scope"),
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
    }


def write_verification(result: dict[str, Any], handoff_dir: Path) -> None:
    json_path = handoff_dir / "sandbox_receipt_handoff_verification.json"
    md_path = handoff_dir / "sandbox_receipt_handoff_verification.md"

    _write_json(json_path, result)

    lines = [
        "# Sandbox Receipt CGE Handoff Verification",
        "",
        f"- Version: `{result['sandbox_receipt_cge_handoff_verification_version']}`",
        f"- Generated: `{result['generated_at_utc']}`",
        f"- Status: **{result['status']}**",
        f"- Verdict: `{result.get('verdict')}`",
        f"- Scope: `{result.get('handoff_scope')}`",
        f"- Execution authority: `{result.get('execution_authority')}`",
        f"- Install authority: `{result.get('install_authority')}`",
        "",
        "## Failed Checks",
        "",
    ]

    if result.get("checks_failed"):
        for item in result["checks_failed"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Passed Checks", ""])
    for item in result.get("checks_passed", []):
        lines.append(f"- `{item}`")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify sandbox receipt CGE handoff")
    parser.add_argument("--handoff-dir", default=str(DEFAULT_HANDOFF_DIR))
    parser.add_argument("--ledger-dir", default=str(DEFAULT_LEDGER_DIR))
    args = parser.parse_args()

    result = verify_handoff(Path(args.handoff_dir), Path(args.ledger_dir))
    write_verification(result, Path(args.handoff_dir))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
