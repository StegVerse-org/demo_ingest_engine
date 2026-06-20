#!/usr/bin/env python3
"""Validate the corrected testing data loop receipt chain."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXPECTED_STEPS = [
    "stegverse_org_ingestion_outbound",
    "stegghost_ingestion_cge_admission",
    "ephemeral_sandbox_batch",
    "stegghost_ingestion_cge_return_validation",
    "stegverse_org_ingestion_return",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()

    try:
        artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"unable to read artifact: {exc}")

    if not isinstance(artifact, dict):
        fail("artifact must be an object")
    dataset_hash = artifact.get("dataset_manifest_hash")
    receipts = artifact.get("receipts")
    if not isinstance(dataset_hash, str) or not dataset_hash:
        fail("dataset_manifest_hash must be a non-empty string")
    if not isinstance(receipts, list):
        fail("receipts must be an array")

    actual_steps = []
    for index, receipt in enumerate(receipts):
        if not isinstance(receipt, dict):
            fail(f"receipt {index} must be an object")
        step_id = receipt.get("step_id")
        receipt_id = receipt.get("receipt_id")
        if not isinstance(step_id, str) or not step_id:
            fail(f"receipt {index} missing step_id")
        if not isinstance(receipt_id, str) or not receipt_id:
            fail(f"receipt {index} missing receipt_id")
        if receipt.get("dataset_manifest_hash") != dataset_hash:
            fail(f"receipt {index} dataset hash mismatch")
        master_records = receipt.get("master_records")
        if not isinstance(master_records, dict):
            fail(f"receipt {index} missing master_records")
        if master_records.get("action_receipt_sent") is not True:
            fail(f"receipt {index} master_records action receipt not sent")
        actual_steps.append(step_id)

    if actual_steps != EXPECTED_STEPS:
        fail("receipt steps do not match corrected loop order")

    print("PASS: testing data loop receipt chain is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
