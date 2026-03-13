from __future__ import annotations
from pathlib import Path
from datetime import datetime
import hashlib
import json

def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def append_event_ledger(root: Path, event_log: dict) -> dict:
    reports_root = root / "reports"
    ledger_dir = reports_root / "event_ledger"
    ledger_dir.mkdir(parents=True, exist_ok=True)

    existing = sorted(ledger_dir.glob("event_batch_*.json"))
    prev_record = None
    if existing:
        prev_record = _load_json(existing[-1])

    prev_batch_id = prev_record["batch_id"] if prev_record else None
    prev_batch_hash = prev_record["batch_hash"] if prev_record else None
    next_idx = len(existing) + 1

    normalized_events = []
    for event in event_log.get("events", []):
        normalized_events.append({
            "event_id": event.get("event_id"),
            "source": event.get("source"),
            "target": event.get("target"),
            "edge": event.get("edge"),
            "permitted": event.get("permitted"),
            "event_type": event.get("event_type"),
            "timestamp_utc": event.get("timestamp_utc"),
        })

    batch_material = json.dumps({
        "previous_batch_hash": prev_batch_hash,
        "event_chain_hash": event_log.get("event_chain_hash"),
        "event_count": event_log.get("event_count"),
        "events": normalized_events,
    }, sort_keys=True)

    batch_hash = _sha256_text(batch_material)

    batch = {
        "ledger_version": "1.0",
        "batch_id": f"event_batch_{next_idx:04d}",
        "previous_batch_id": prev_batch_id,
        "previous_batch_hash": prev_batch_hash,
        "event_chain_hash": event_log.get("event_chain_hash"),
        "event_count": event_log.get("event_count"),
        "batch_hash": batch_hash,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "events": normalized_events,
    }

    batch_path = ledger_dir / f"{batch['batch_id']}.json"
    batch_path.write_text(json.dumps(batch, indent=2), encoding="utf-8")

    latest = {
        "latest_batch_id": batch["batch_id"],
        "latest_batch_hash": batch_hash,
    }
    (ledger_dir / "latest_event_batch.json").write_text(json.dumps(latest, indent=2), encoding="utf-8")

    lines = []
    for p in sorted(ledger_dir.glob("event_batch_*.json")):
        data = _load_json(p)
        lines.append(
            f"{data['batch_id']} | prev={data.get('previous_batch_id')} | hash={data['batch_hash']} | events={data['event_count']}"
        )
    (ledger_dir / "event_ledger_chain.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    return batch

def verify_event_ledger(root: Path) -> dict:
    reports_root = root / "reports"
    ledger_dir = reports_root / "event_ledger"
    if not ledger_dir.exists():
        return {
            "ledger_verification_version": "1.0",
            "status": "FAIL",
            "checks_passed": [],
            "checks_failed": ["event_ledger_missing"],
        }

    batches = sorted(ledger_dir.glob("event_batch_*.json"))
    checks_passed = []
    checks_failed = []

    prev_id = None
    prev_hash = None
    for batch_file in batches:
        batch = _load_json(batch_file)

        if prev_id is None:
            if batch.get("previous_batch_id") is None:
                checks_passed.append(f"ledger_root_ok:{batch['batch_id']}")
            else:
                checks_failed.append(f"ledger_root_invalid:{batch['batch_id']}")
        else:
            if batch.get("previous_batch_id") == prev_id:
                checks_passed.append(f"ledger_prev_id_ok:{batch['batch_id']}")
            else:
                checks_failed.append(f"ledger_prev_id_mismatch:{batch['batch_id']}")
            if batch.get("previous_batch_hash") == prev_hash:
                checks_passed.append(f"ledger_prev_hash_ok:{batch['batch_id']}")
            else:
                checks_failed.append(f"ledger_prev_hash_mismatch:{batch['batch_id']}")

        normalized_events = []
        for event in batch.get("events", []):
            normalized_events.append({
                "event_id": event.get("event_id"),
                "source": event.get("source"),
                "target": event.get("target"),
                "edge": event.get("edge"),
                "permitted": event.get("permitted"),
                "event_type": event.get("event_type"),
                "timestamp_utc": event.get("timestamp_utc"),
            })

        recomputed_material = json.dumps({
            "previous_batch_hash": batch.get("previous_batch_hash"),
            "event_chain_hash": batch.get("event_chain_hash"),
            "event_count": batch.get("event_count"),
            "events": normalized_events,
        }, sort_keys=True)
        recomputed_hash = _sha256_text(recomputed_material)
        if recomputed_hash == batch.get("batch_hash"):
            checks_passed.append(f"ledger_batch_hash_ok:{batch['batch_id']}")
        else:
            checks_failed.append(f"ledger_batch_hash_mismatch:{batch['batch_id']}")

        prev_id = batch.get("batch_id")
        prev_hash = batch.get("batch_hash")

    return {
        "ledger_verification_version": "1.0",
        "status": "PASS" if not checks_failed else "FAIL",
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "batch_count": len(batches),
    }

def write_event_ledger_reports(root: Path, batch: dict, verification: dict):
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    (reports_root / "event_ledger_receipt.json").write_text(json.dumps(batch, indent=2), encoding="utf-8")
    (reports_root / "event_ledger_verification.json").write_text(json.dumps(verification, indent=2), encoding="utf-8")

    lines = [
        "# Event Ledger Verification",
        "",
        f"- Status: **{verification['status']}**",
        f"- Batch count: `{verification.get('batch_count', 0)}`",
        f"- Latest batch: `{batch.get('batch_id')}`",
        f"- Latest batch hash: `{batch.get('batch_hash')}`",
        "",
    ]
    (reports_root / "event_ledger_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")