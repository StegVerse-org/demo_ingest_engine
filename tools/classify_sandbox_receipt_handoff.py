from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HANDOFF_VERSION = "1.0"
DEFAULT_LEDGER_DIR = Path("event_ledger")
DEFAULT_HANDOFF_DIR = Path("cge_handoff")


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


def classify(latest_batch: dict[str, Any], ledger_verification: dict[str, Any]) -> tuple[str, list[str], list[str]]:
    reasons: list[str] = []
    constraints: list[str] = [
        "observe_only_handoff",
        "no_execution_authority",
        "no_install_authority",
        "cge_must_revalidate_before_action",
    ]

    if ledger_verification.get("status") != "PASS":
        reasons.append("ledger_verification_not_pass")
        return "BLOCKED_EXECUTION", reasons, constraints

    if latest_batch.get("verification_status") != "PASS":
        reasons.append("latest_batch_verification_not_pass")
        return "BLOCKED_EXECUTION", reasons, constraints

    if latest_batch.get("fail_closed_count", 0) > 0:
        reasons.append("one_or_more_packets_failed_closed")

    if latest_batch.get("admitted_count", 0) > 0:
        reasons.append("one_or_more_packets_admitted_for_review")
        return "READY_FOR_REVIEW", reasons, constraints

    reasons.append("no_admitted_packets_in_latest_batch")
    return "OBSERVE_ONLY", reasons, constraints


def build_handoff(ledger_dir: Path) -> dict[str, Any]:
    latest_path = ledger_dir / "latest_sandbox_receipt_batch.json"
    ledger_verification_path = ledger_dir / "sandbox_receipt_ledger_verification.json"

    latest_batch = _load_json(latest_path)
    ledger_verification = _load_json(ledger_verification_path)
    verdict, reasons, constraints = classify(latest_batch, ledger_verification)

    return {
        "sandbox_receipt_cge_handoff_version": HANDOFF_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "event_ledger/latest_sandbox_receipt_batch.json",
        "source_sha256": _sha256_file(latest_path),
        "ledger_verification_source": "event_ledger/sandbox_receipt_ledger_verification.json",
        "ledger_verification_sha256": _sha256_file(ledger_verification_path),
        "handoff_target": "CGE",
        "handoff_scope": "classification_only",
        "execution_authority": False,
        "install_authority": False,
        "verdict": verdict,
        "reasons": reasons,
        "constraints": constraints,
        "latest_batch": {
            "batch_number": latest_batch.get("batch_number"),
            "batch_sha256": latest_batch.get("batch_sha256"),
            "previous_batch_sha256": latest_batch.get("previous_batch_sha256"),
            "receipt_count": latest_batch.get("receipt_count"),
            "admitted_count": latest_batch.get("admitted_count"),
            "fail_closed_count": latest_batch.get("fail_closed_count"),
            "verification_status": latest_batch.get("verification_status"),
        },
        "ledger_verification": {
            "status": ledger_verification.get("status"),
            "batch_count": ledger_verification.get("batch_count"),
            "latest_batch": ledger_verification.get("latest_batch"),
        },
    }


def write_handoff(handoff: dict[str, Any], handoff_dir: Path) -> None:
    handoff_dir.mkdir(parents=True, exist_ok=True)
    handoff_json = handoff_dir / "sandbox_receipt_handoff.json"
    handoff_md = handoff_dir / "sandbox_receipt_handoff.md"

    _write_json(handoff_json, handoff)

    lines = [
        "# Sandbox Receipt CGE Handoff",
        "",
        f"- Version: `{handoff['sandbox_receipt_cge_handoff_version']}`",
        f"- Created: `{handoff['created_at_utc']}`",
        f"- Target: `{handoff['handoff_target']}`",
        f"- Scope: `{handoff['handoff_scope']}`",
        f"- Verdict: **{handoff['verdict']}**",
        f"- Execution authority: `{handoff['execution_authority']}`",
        f"- Install authority: `{handoff['install_authority']}`",
        f"- Source SHA-256: `{handoff['source_sha256']}`",
        f"- Ledger verification SHA-256: `{handoff['ledger_verification_sha256']}`",
        "",
        "## Reasons",
        "",
    ]

    for reason in handoff.get("reasons", []):
        lines.append(f"- `{reason}`")

    lines.extend(["", "## Constraints", ""])
    for constraint in handoff.get("constraints", []):
        lines.append(f"- `{constraint}`")

    latest = handoff.get("latest_batch", {})
    lines.extend(
        [
            "",
            "## Latest Ledger Batch",
            "",
            f"- Batch number: `{latest.get('batch_number')}`",
            f"- Batch SHA-256: `{latest.get('batch_sha256')}`",
            f"- Previous batch SHA-256: `{latest.get('previous_batch_sha256')}`",
            f"- Receipt count: `{latest.get('receipt_count')}`",
            f"- Admitted count: `{latest.get('admitted_count')}`",
            f"- Fail-closed count: `{latest.get('fail_closed_count')}`",
            f"- Verification status: `{latest.get('verification_status')}`",
        ]
    )

    handoff_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify sandbox receipt ledger for CGE handoff")
    parser.add_argument("--ledger-dir", default=str(DEFAULT_LEDGER_DIR))
    parser.add_argument("--handoff-dir", default=str(DEFAULT_HANDOFF_DIR))
    args = parser.parse_args()

    handoff = build_handoff(Path(args.ledger_dir))
    write_handoff(handoff, Path(args.handoff_dir))
    print(json.dumps(handoff, indent=2, sort_keys=True))
    return 0 if handoff.get("verdict") in {"OBSERVE_ONLY", "READY_FOR_REVIEW"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
