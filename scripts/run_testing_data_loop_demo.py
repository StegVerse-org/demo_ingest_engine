#!/usr/bin/env python3
"""Run the corrected testing data loop as a local receipt-chain demo.

This demo exercises the StegVerse-org portions directly and emits the expected
StegGhost receipt shapes inline so the full org -> sandbox -> org receipt chain
can be inspected without cross-repository imports.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ORG_STEPS = {
    "stegverse_org_ingestion_outbound": "org outbound ingestion receipt",
    "stegverse_org_ingestion_return": "org return ingestion receipt",
}

SANDBOX_STEPS = {
    "stegghost_ingestion_cge_admission": "sandbox intake CGE receipt",
    "ephemeral_sandbox_batch": "ephemeral sandbox execution receipt",
    "stegghost_ingestion_cge_return_validation": "sandbox return CGE receipt",
}

DATASET_HASH = "sha256:0000000000000000000000000000000000000000000000000000000000000000"


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def receipt_id(step_id: str, dataset_hash: str, timestamp: str) -> str:
    digest = hashlib.sha256(f"{step_id}|{dataset_hash}|{timestamp}".encode("utf-8")).hexdigest()[:16]
    return f"{step_id}-{digest}"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_receipt(step_id: str, receipt_type: str, dataset_hash: str, previous: list[dict[str, str]]) -> dict:
    timestamp = now()
    rid = receipt_id(step_id, dataset_hash, timestamp)
    mrid = "mr-" + rid
    return {
        "step_id": step_id,
        "receipt_id": rid,
        "receipt_type": receipt_type,
        "dataset_manifest_hash": dataset_hash,
        "timestamp": timestamp,
        "previous_receipts": previous,
        "master_records": {
            "action_receipt_sent": True,
            "action_receipt_id": mrid,
            "action_receipt_hash": sha256_text(f"{mrid}|{rid}|{dataset_hash}|{timestamp}"),
        },
    }


def compact(receipt: dict) -> dict[str, str]:
    return {"step_id": receipt["step_id"], "receipt_id": receipt["receipt_id"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dataset-manifest-hash", default=DATASET_HASH)
    args = parser.parse_args()

    previous = [
        {"step_id": "human_input", "receipt_id": "human-intake-receipt-001"},
        {"step_id": "sdk_or_llm_adapter_intake", "receipt_id": "sdk-intake-receipt-001"},
    ]

    chain: list[dict] = []

    outbound = make_receipt(
        "stegverse_org_ingestion_outbound",
        ORG_STEPS["stegverse_org_ingestion_outbound"],
        args.dataset_manifest_hash,
        previous,
    )
    chain.append(outbound)

    sandbox_previous = previous + [compact(outbound)]
    admission = make_receipt(
        "stegghost_ingestion_cge_admission",
        SANDBOX_STEPS["stegghost_ingestion_cge_admission"],
        args.dataset_manifest_hash,
        sandbox_previous,
    )
    chain.append(admission)

    batch = make_receipt(
        "ephemeral_sandbox_batch",
        SANDBOX_STEPS["ephemeral_sandbox_batch"],
        args.dataset_manifest_hash,
        sandbox_previous + [compact(admission)],
    )
    chain.append(batch)

    return_validation = make_receipt(
        "stegghost_ingestion_cge_return_validation",
        SANDBOX_STEPS["stegghost_ingestion_cge_return_validation"],
        args.dataset_manifest_hash,
        sandbox_previous + [compact(admission), compact(batch)],
    )
    chain.append(return_validation)

    org_return = make_receipt(
        "stegverse_org_ingestion_return",
        ORG_STEPS["stegverse_org_ingestion_return"],
        args.dataset_manifest_hash,
        sandbox_previous + [compact(admission), compact(batch), compact(return_validation)],
    )
    chain.append(org_return)

    artifact = {
        "loop_id": "local-testing-data-loop-demo",
        "dataset_manifest_hash": args.dataset_manifest_hash,
        "receipts": chain,
        "status": "complete_receipt_chain_generated",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
