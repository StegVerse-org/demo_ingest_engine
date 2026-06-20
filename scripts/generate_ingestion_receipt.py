#!/usr/bin/env python3
"""Generate StegVerse-org testing data ingestion receipts.

This command emits the minimal org ingestion receipt shape enforced by
validate_ingestion_receipts.py and gate_ingestion_handoff.py.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

VALID_STEPS = {
    "stegverse_org_ingestion_outbound": "org outbound ingestion receipt",
    "stegverse_org_ingestion_return": "org return ingestion receipt",
}


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_receipt_id(step_id: str, dataset_manifest_hash: str, timestamp: str) -> str:
    digest = hashlib.sha256(f"{step_id}|{dataset_manifest_hash}|{timestamp}".encode("utf-8")).hexdigest()[:16]
    return f"{step_id}-{digest}"


def load_previous_receipts(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("previous receipts file must contain an array")
    receipts: list[dict[str, str]] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise SystemExit(f"previous receipt {index} must be an object")
        step_id = item.get("step_id")
        receipt_id = item.get("receipt_id")
        if not isinstance(step_id, str) or not step_id:
            raise SystemExit(f"previous receipt {index} missing step_id")
        if not isinstance(receipt_id, str) or not receipt_id:
            raise SystemExit(f"previous receipt {index} missing receipt_id")
        receipts.append({"step_id": step_id, "receipt_id": receipt_id})
    return receipts


def build_receipt(step_id: str, dataset_manifest_hash: str, previous_receipts: list[dict[str, str]]) -> dict:
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    receipt_id = stable_receipt_id(step_id, dataset_manifest_hash, timestamp)
    master_records_id = "mr-" + receipt_id
    master_payload = f"{master_records_id}|{receipt_id}|{dataset_manifest_hash}|{timestamp}"

    return {
        "step_id": step_id,
        "receipt_id": receipt_id,
        "receipt_type": VALID_STEPS[step_id],
        "dataset_manifest_hash": dataset_manifest_hash,
        "timestamp": timestamp,
        "previous_receipts": previous_receipts,
        "master_records": {
            "action_receipt_sent": True,
            "action_receipt_id": master_records_id,
            "action_receipt_hash": sha256_text(master_payload),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step-id", required=True, choices=sorted(VALID_STEPS))
    parser.add_argument("--dataset-manifest-hash", required=True)
    parser.add_argument("--previous-receipts", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    previous_receipts = load_previous_receipts(args.previous_receipts)
    receipt = build_receipt(args.step_id, args.dataset_manifest_hash, previous_receipts)
    output = json.dumps(receipt, indent=2, sort_keys=True) + "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
