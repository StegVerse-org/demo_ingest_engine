#!/usr/bin/env python3
"""Gate StegVerse-org testing data ingestion handoffs.

This command validates an org ingestion receipt and prints the next permitted
step. It fails closed when the receipt is incomplete or the requested handoff
is not an allowed org ingestion handoff.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validate_ingestion_receipts import validate_receipt

ALLOWED_HANDOFFS = {
    "stegverse_org_ingestion_outbound": "stegghost_ingestion_cge_admission",
    "stegverse_org_ingestion_return": "human_delivery",
}


def fail(message: str) -> None:
    print(f"DENY: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{name} must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="Path to org ingestion receipt JSON")
    parser.add_argument("--next-step", required=True, help="Requested next step")
    args = parser.parse_args()

    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {exc}")
    except OSError as exc:
        fail(f"unable to read receipt: {exc}")

    receipt_obj = require_object(receipt, "receipt")
    validate_receipt(receipt_obj)

    current_step = receipt_obj["step_id"]
    expected_next = ALLOWED_HANDOFFS[current_step]
    if args.next_step != expected_next:
        fail(f"next step must be {expected_next} for {current_step}")

    print(f"ALLOW: {current_step} may hand off to {expected_next}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
