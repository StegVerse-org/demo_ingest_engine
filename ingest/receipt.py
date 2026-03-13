from __future__ import annotations
from pathlib import Path
from datetime import datetime
import hashlib
import json

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def write_receipts(reports_root: Path, report: dict, source_path: Path, manifest: dict | None, governance_receipt: dict | None):
    reports_root.mkdir(parents=True, exist_ok=True)

    bundle_hash = sha256_file(source_path) if source_path.is_file() else sha256_text(str(source_path.resolve()))
    manifest_hash = sha256_text(json.dumps(manifest, sort_keys=True)) if manifest else None
    governance_hash = sha256_text(json.dumps(governance_receipt, sort_keys=True)) if governance_receipt else None
    report_hash = sha256_text(json.dumps(report, sort_keys=True))

    state_before = sha256_text(f"{report.get('mode')}|before|{bundle_hash}")
    state_after = sha256_text(f"{report.get('mode')}|after|{report_hash}|{governance_hash or 'none'}")

    execution_receipt = {
        "receipt_version": "1.0",
        "engine": "demo_ingest_engine",
        "mode": report.get("mode"),
        "source": str(source_path),
        "bundle_hash": bundle_hash,
        "manifest_hash": manifest_hash,
        "governance_hash": governance_hash,
        "state_hash_before": state_before,
        "state_hash_after": state_after,
        "report_hash": report_hash,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

    (reports_root / "execution_receipt.json").write_text(
        json.dumps(execution_receipt, indent=2), encoding="utf-8"
    )
    (reports_root / "artifact_hash.txt").write_text(bundle_hash + "\n", encoding="utf-8")
    (reports_root / "state_hash.txt").write_text(state_after + "\n", encoding="utf-8")
