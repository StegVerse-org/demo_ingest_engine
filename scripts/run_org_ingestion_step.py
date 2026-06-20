#!/usr/bin/env python3
"""Run a minimal StegVerse-org testing data ingestion step.

The runner generates an org ingestion receipt, validates it, gates the requested
handoff, and writes the receipt only after the gate passes.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from gate_ingestion_handoff import main as gate_main
from generate_ingestion_receipt import build_receipt, load_previous_receipts
from validate_ingestion_receipts import validate_receipt

NEXT_STEPS = {
    "stegverse_org_ingestion_outbound": "stegghost_ingestion_cge_admission",
    "stegverse_org_ingestion_return": "human_delivery",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step-id", required=True, choices=sorted(NEXT_STEPS))
    parser.add_argument("--dataset-manifest-hash", required=True)
    parser.add_argument("--previous-receipts", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    previous_receipts = load_previous_receipts(args.previous_receipts)
    receipt = build_receipt(args.step_id, args.dataset_manifest_hash, previous_receipts)
    validate_receipt(receipt)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tmp:
        import json

        json.dump(receipt, tmp, indent=2, sort_keys=True)
        tmp.write("\n")
        tmp_path = Path(tmp.name)

    import sys

    old_argv = sys.argv
    try:
        sys.argv = [
            "gate_ingestion_handoff.py",
            str(tmp_path),
            "--next-step",
            NEXT_STEPS[args.step_id],
        ]
        gate_main()
    finally:
        sys.argv = old_argv

    args.output.write_text(tmp_path.read_text(encoding="utf-8"), encoding="utf-8")
    tmp_path.unlink(missing_ok=True)
    print(f"WROTE: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
