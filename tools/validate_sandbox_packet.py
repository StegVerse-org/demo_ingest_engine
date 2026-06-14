from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


EXPECTED = {
    "schema": "stegverse.entity_sandbox_bridge.v1",
    "sender_repository": "StegGhost/entity-sandbox-runner",
    "receiver_repository": "StegVerse-org/demo_ingest_engine",
}

ALLOWED_REQUESTED_MODES = {"plan", "review", "install"}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _packet_hash(packet: Any) -> str:
    payload = json.dumps(packet, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_packet(packet: Any) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []

    if not isinstance(packet, dict):
        return [
            {
                "field": "packet",
                "expected": "object",
                "actual": type(packet).__name__,
            }
        ]

    for key, expected_value in EXPECTED.items():
        actual_value = packet.get(key)
        if actual_value != expected_value:
            errors.append(
                {
                    "field": key,
                    "expected": expected_value,
                    "actual": actual_value,
                }
            )

    boundary = packet.get("boundary", {})
    if not isinstance(boundary, dict):
        errors.append(
            {
                "field": "boundary",
                "expected": "object",
                "actual": type(boundary).__name__,
            }
        )
        boundary = {}

    if boundary.get("sender_may_install_into_receiver") is not False:
        errors.append(
            {
                "field": "boundary.sender_may_install_into_receiver",
                "expected": False,
                "actual": boundary.get("sender_may_install_into_receiver"),
            }
        )

    if boundary.get("receiver_must_fail_closed_on_install_request") is not True:
        errors.append(
            {
                "field": "boundary.receiver_must_fail_closed_on_install_request",
                "expected": True,
                "actual": boundary.get("receiver_must_fail_closed_on_install_request"),
            }
        )

    requested_mode = packet.get("requested_mode", "review")
    if requested_mode not in ALLOWED_REQUESTED_MODES:
        errors.append(
            {
                "field": "requested_mode",
                "expected": sorted(ALLOWED_REQUESTED_MODES),
                "actual": requested_mode,
            }
        )

    if requested_mode == "install":
        errors.append(
            {
                "field": "requested_mode",
                "expected": "plan_or_review_only",
                "actual": requested_mode,
            }
        )

    return errors


def build_receipt(packet: Any, errors: list[dict[str, Any]]) -> dict[str, Any]:
    requested_mode = packet.get("requested_mode", "review") if isinstance(packet, dict) else None

    return {
        "schema": "stegverse.org_sandbox_receipt_admission.v1",
        "received_at_unix": time.time(),
        "receiver_repository": "StegVerse-org/demo_ingest_engine",
        "sender_repository": packet.get("sender_repository") if isinstance(packet, dict) else None,
        "requested_mode": requested_mode,
        "admitted": len(errors) == 0,
        "verdict": "RECEIVED_FOR_REVIEW" if len(errors) == 0 else "FAIL_CLOSED",
        "errors": errors,
        "packet_sha256": _packet_hash(packet),
        "packet": packet,
    }


def write_receipt(receipt: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_ts = str(int(receipt["received_at_unix"] * 1000))
    out_path = out_dir / f"stegghost_{safe_ts}.receipt.json"
    out_path.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate StegGhost sandbox bridge packet")
    parser.add_argument("--packet", required=True, help="Path to bridge packet JSON")
    parser.add_argument(
        "--out-dir",
        default="reports/sandbox_receipts",
        help="Directory where admission receipt should be written",
    )
    parser.add_argument(
        "--receipt-path-file",
        default="receipt_path.txt",
        help="Path where the generated receipt path should be written",
    )
    args = parser.parse_args()

    packet_path = Path(args.packet)
    packet = _load_json(packet_path)

    errors = validate_packet(packet)
    receipt = build_receipt(packet, errors)
    receipt_path = write_receipt(receipt, Path(args.out_dir))

    Path(args.receipt_path_file).write_text(str(receipt_path), encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
