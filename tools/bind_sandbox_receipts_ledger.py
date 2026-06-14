from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LEDGER_BINDING_VERSION = "1.0"
DEFAULT_RECEIPTS_DIR = Path("reports/sandbox_receipts")
DEFAULT_LEDGER_DIR = Path("event_ledger")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sha256_json(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _existing_batches(ledger_dir: Path) -> list[Path]:
    return sorted(ledger_dir.glob("sandbox_receipt_batch_*.json"))


def _next_batch_number(ledger_dir: Path) -> int:
    max_seen = 0
    for path in _existing_batches(ledger_dir):
        stem = path.stem
        try:
            value = int(stem.rsplit("_", 1)[1])
            max_seen = max(max_seen, value)
        except Exception:
            continue
    return max_seen + 1


def _latest_batch_hash(ledger_dir: Path) -> str | None:
    latest_path = ledger_dir / "latest_sandbox_receipt_batch.json"
    if not latest_path.exists():
        return None
    try:
        latest = _load_json(latest_path)
        return latest.get("batch_sha256")
    except Exception:
        return None


def build_batch(receipts_dir: Path, ledger_dir: Path) -> dict[str, Any]:
    index_path = receipts_dir / "sandbox_receipt_index.json"
    verification_path = receipts_dir / "sandbox_receipt_index_verification.json"

    index = _load_json(index_path)
    verification = _load_json(verification_path)

    batch_number = _next_batch_number(ledger_dir)
    previous_batch_sha256 = _latest_batch_hash(ledger_dir)

    batch = {
        "sandbox_receipt_ledger_batch_version": LEDGER_BINDING_VERSION,
        "batch_number": batch_number,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "sandbox_receipt_index_verification",
        "receipts_dir": str(receipts_dir),
        "index_path": str(index_path),
        "index_sha256": _sha256_file(index_path),
        "verification_path": str(verification_path),
        "verification_sha256": _sha256_file(verification_path),
        "verification_status": verification.get("status"),
        "receipt_count": index.get("receipt_count"),
        "admitted_count": index.get("admitted_count"),
        "fail_closed_count": index.get("fail_closed_count"),
        "latest_receipt": index.get("latest_receipt"),
        "previous_batch_sha256": previous_batch_sha256,
    }
    batch["batch_sha256"] = _sha256_json(batch)
    return batch


def verify_ledger(ledger_dir: Path) -> dict[str, Any]:
    checks_passed: list[str] = []
    checks_failed: list[str] = []
    batches: list[dict[str, Any]] = []

    batch_files = _existing_batches(ledger_dir)
    previous_hash: str | None = None

    for expected_number, path in enumerate(batch_files, start=1):
        try:
            batch = _load_json(path)
        except Exception as exc:
            checks_failed.append(f"batch_unparseable:{path.name}:{type(exc).__name__}")
            continue

        recorded_hash = batch.get("batch_sha256")
        batch_without_hash = dict(batch)
        batch_without_hash.pop("batch_sha256", None)
        recomputed_hash = _sha256_json(batch_without_hash)

        if recorded_hash == recomputed_hash:
            checks_passed.append(f"batch_hash_matches:{path.name}")
        else:
            checks_failed.append(f"batch_hash_mismatch:{path.name}")

        if batch.get("batch_number") == expected_number:
            checks_passed.append(f"batch_number_matches:{path.name}")
        else:
            checks_failed.append(f"batch_number_mismatch:{path.name}:expected={expected_number}:actual={batch.get('batch_number')}")

        if batch.get("previous_batch_sha256") == previous_hash:
            checks_passed.append(f"previous_hash_matches:{path.name}")
        else:
            checks_failed.append(f"previous_hash_mismatch:{path.name}")

        if batch.get("verification_status") == "PASS":
            checks_passed.append(f"verification_status_pass:{path.name}")
        else:
            checks_failed.append(f"verification_status_not_pass:{path.name}:{batch.get('verification_status')}")

        previous_hash = recorded_hash
        batches.append(
            {
                "path": str(path),
                "batch_number": batch.get("batch_number"),
                "batch_sha256": recorded_hash,
                "previous_batch_sha256": batch.get("previous_batch_sha256"),
                "receipt_count": batch.get("receipt_count"),
                "admitted_count": batch.get("admitted_count"),
                "fail_closed_count": batch.get("fail_closed_count"),
                "verification_status": batch.get("verification_status"),
            }
        )

    latest_path = ledger_dir / "latest_sandbox_receipt_batch.json"
    if latest_path.exists():
        latest = _load_json(latest_path)
        if batches and latest.get("batch_sha256") == batches[-1].get("batch_sha256"):
            checks_passed.append("latest_pointer_matches_last_batch")
        elif not batches:
            checks_failed.append("latest_pointer_exists_without_batches")
        else:
            checks_failed.append("latest_pointer_mismatch")
    else:
        checks_failed.append("latest_pointer_missing")

    return {
        "sandbox_receipt_ledger_verification_version": LEDGER_BINDING_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "ledger_dir": str(ledger_dir),
        "status": "PASS" if not checks_failed else "FAIL",
        "batch_count": len(batches),
        "latest_batch": batches[-1] if batches else None,
        "batches": batches,
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
    }


def write_batch_and_verification(batch: dict[str, Any], ledger_dir: Path) -> dict[str, Any]:
    ledger_dir.mkdir(parents=True, exist_ok=True)
    batch_path = ledger_dir / f"sandbox_receipt_batch_{int(batch['batch_number']):06d}.json"
    latest_path = ledger_dir / "latest_sandbox_receipt_batch.json"

    _write_json(batch_path, batch)
    _write_json(latest_path, batch)

    verification = verify_ledger(ledger_dir)
    _write_json(ledger_dir / "sandbox_receipt_ledger_verification.json", verification)

    lines = [
        "# Sandbox Receipt Ledger Verification",
        "",
        f"- Version: `{verification['sandbox_receipt_ledger_verification_version']}`",
        f"- Generated: `{verification['generated_at_utc']}`",
        f"- Status: **{verification['status']}**",
        f"- Batch count: `{verification['batch_count']}`",
        "",
        "## Latest Batch",
        "",
    ]

    latest = verification.get("latest_batch")
    if latest:
        lines.extend(
            [
                f"- Batch number: `{latest.get('batch_number')}`",
                f"- Batch SHA-256: `{latest.get('batch_sha256')}`",
                f"- Previous batch SHA-256: `{latest.get('previous_batch_sha256')}`",
                f"- Receipt count: `{latest.get('receipt_count')}`",
                f"- Verification status: `{latest.get('verification_status')}`",
                "",
            ]
        )
    else:
        lines.extend(["- none", ""])

    lines.extend(["## Failed Checks", ""])
    if verification.get("checks_failed"):
        for item in verification["checks_failed"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Passed Checks", ""])
    for item in verification.get("checks_passed", []):
        lines.append(f"- `{item}`")

    (ledger_dir / "sandbox_receipt_ledger_verification.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return verification


def main() -> int:
    parser = argparse.ArgumentParser(description="Bind verified sandbox receipt index to event ledger")
    parser.add_argument("--receipts-dir", default=str(DEFAULT_RECEIPTS_DIR))
    parser.add_argument("--ledger-dir", default=str(DEFAULT_LEDGER_DIR))
    args = parser.parse_args()

    receipts_dir = Path(args.receipts_dir)
    ledger_dir = Path(args.ledger_dir)
    batch = build_batch(receipts_dir, ledger_dir)
    verification = write_batch_and_verification(batch, ledger_dir)

    print(json.dumps({"batch": batch, "verification": verification}, indent=2, sort_keys=True))
    return 0 if verification.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
