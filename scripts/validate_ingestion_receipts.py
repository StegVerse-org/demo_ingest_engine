#!/usr/bin/env python3
"""Validate StegVerse-org testing data ingestion receipts.

The validator checks the minimum receipt shape needed before the ingestion
surface advances testing data through the corrected loop.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SHA256_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
VALID_STEPS = {
    "stegverse_org_ingestion_outbound": "org outbound ingestion receipt",
    "stegverse_org_ingestion_return": "org return ingestion receipt",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        fail(f"{name} must be a non-empty string")
    return value


def validate_hash(value: Any, name: str) -> None:
    text = require_string(value, name)
    if not SHA256_RE.match(text):
        fail(f"{name} must match sha256:<64 lowercase hex chars>")


def validate_receipt(receipt: dict[str, Any]) -> None:
    step_id = require_string(receipt.get("step_id"), "step_id")
    if step_id not in VALID_STEPS:
        fail("step_id must be a StegVerse-org ingestion step")

    require_string(receipt.get("receipt_id"), "receipt_id")
    validate_hash(receipt.get("dataset_manifest_hash"), "dataset_manifest_hash")

    receipt_type = require_string(receipt.get("receipt_type"), "receipt_type")
    if receipt_type != VALID_STEPS[step_id]:
        fail(f"receipt_type must be {VALID_STEPS[step_id]} for {step_id}")

    mr = receipt.get("master_records")
    if not isinstance(mr, dict):
        fail("master_records must be an object")
    if mr.get("action_receipt_sent") is not True:
        fail("master_records.action_receipt_sent must be true")
    require_string(mr.get("action_receipt_id"), "master_records.action_receipt_id")
    if "action_receipt_hash" in mr:
        validate_hash(mr.get("action_receipt_hash"), "master_records.action_receipt_hash")

    previous = receipt.get("previous_receipts", [])
    if not isinstance(previous, list):
        fail("previous_receipts must be an array")
    for index, item in enumerate(previous):
        if not isinstance(item, dict):
            fail(f"previous_receipts[{index}] must be an object")
        require_string(item.get("step_id"), f"previous_receipts[{index}].step_id")
        require_string(item.get("receipt_id"), f"previous_receipts[{index}].receipt_id")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="Path to ingestion receipt JSON")
    args = parser.parse_args()

    try:
        data = json.loads(args.receipt.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {exc}")
    except OSError as exc:
        fail(f"unable to read receipt: {exc}")

    if not isinstance(data, dict):
        fail("receipt must be an object")
    validate_receipt(data)
    print("PASS: ingestion receipt is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
