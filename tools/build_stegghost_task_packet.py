from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PACKET_VERSION = "1.0"
DEFAULT_RECEIPT_PATH = Path("manifest_receipts/latest_declared_task_manifest_receipt.json")
DEFAULT_OUT_DIR = Path("stegghost_dispatch")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_task_packet(receipt_path: Path) -> dict[str, Any]:
    receipt = _load_json(receipt_path)

    if receipt.get("verdict") != "ADMISSIBLE_TEST_TASK" or receipt.get("admissible") is not True:
        raise ValueError("task packet requires an ADMISSIBLE_TEST_TASK receipt")

    if receipt.get("route_to_stegghost_ingestion") is not True:
        raise ValueError("receipt does not allow routing to StegGhost ingestion")

    return {
        "stegghost_task_packet_version": PACKET_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "schema": "stegverse.stegghost_task_packet.v1",
        "source": "StegVerse-org",
        "recipient": "StegGhost ingestion",
        "route_authority": "route_only",
        "route_allowed": True,
        "manifest_receipt_path": str(receipt_path),
        "manifest_receipt_sha256": _sha256_file(receipt_path),
        "active_path": receipt.get("active_path"),
        "submitter": receipt.get("submitter"),
        "target": receipt.get("target"),
        "test": receipt.get("test"),
        "result_receipt_required": True,
        "return_result_to_submitter": True,
        "install_authority": False,
        "outside_sandbox_authority": False,
        "planning_authority": False,
        "conversation_loop_allowed": False,
        "repository_mutation_allowed": False,
        "blocked_actions": [
            "install",
            "outside_sandbox_action",
            "plan",
            "review",
            "governance_review",
            "mutate_repository",
            "conversation_loop"
        ]
    }


def write_task_packet(packet: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_path = out_dir / "latest_stegghost_task_packet.json"
    receipt_path = out_dir / "latest_stegghost_task_packet_receipt.json"
    md_path = out_dir / "latest_stegghost_task_packet.md"

    _write_json(packet_path, packet)

    task_receipt = {
        "stegghost_task_packet_receipt_version": PACKET_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "task_packet_path": str(packet_path),
        "task_packet_sha256": _sha256_file(packet_path),
        "route_allowed": packet.get("route_allowed"),
        "route_authority": packet.get("route_authority"),
        "recipient": packet.get("recipient"),
        "result_receipt_required": packet.get("result_receipt_required"),
        "return_result_to_submitter": packet.get("return_result_to_submitter"),
        "install_authority": packet.get("install_authority"),
        "outside_sandbox_authority": packet.get("outside_sandbox_authority"),
        "planning_authority": packet.get("planning_authority"),
        "conversation_loop_allowed": packet.get("conversation_loop_allowed"),
    }
    _write_json(receipt_path, task_receipt)

    lines = [
        "# StegGhost Task Packet",
        "",
        f"- Route allowed: `{packet.get('route_allowed')}`",
        f"- Route authority: `{packet.get('route_authority')}`",
        f"- Recipient: `{packet.get('recipient')}`",
        f"- Result receipt required: `{packet.get('result_receipt_required')}`",
        f"- Return result to submitter: `{packet.get('return_result_to_submitter')}`",
        f"- Install authority: `{packet.get('install_authority')}`",
        f"- Outside sandbox authority: `{packet.get('outside_sandbox_authority')}`",
        f"- Planning authority: `{packet.get('planning_authority')}`",
        f"- Conversation loop allowed: `{packet.get('conversation_loop_allowed')}`",
        "",
        "## Blocked Actions",
        "",
    ]
    for item in packet.get("blocked_actions", []):
        lines.append(f"- `{item}`")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return packet_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build route-only StegGhost task packet from admissible manifest receipt")
    parser.add_argument("--receipt", default=str(DEFAULT_RECEIPT_PATH))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--task-path-file")
    args = parser.parse_args()

    packet = build_task_packet(Path(args.receipt))
    out_path = write_task_packet(packet, Path(args.out_dir))

    if args.task_path_file:
        Path(args.task_path_file).write_text(str(out_path), encoding="utf-8")

    print(json.dumps({"task_packet_path": str(out_path), "task_packet": packet}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
