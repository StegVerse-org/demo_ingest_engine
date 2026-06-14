from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


QUEUE_VERSION = "1.0"
DEFAULT_HANDOFF_DIR = Path("cge_handoff")
DEFAULT_QUEUE_DIR = Path("cge_intake")


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


def _make_queue_item(handoff: dict[str, Any], verification: dict[str, Any], handoff_path: Path, verification_path: Path) -> dict[str, Any]:
    verdict = handoff.get("verdict")
    status = "QUEUED_FOR_REVIEW" if verdict == "READY_FOR_REVIEW" else "OBSERVE_ONLY"
    if verification.get("status") != "PASS" or verdict == "BLOCKED_EXECUTION":
        status = "BLOCKED"

    latest_batch = handoff.get("latest_batch", {}) if isinstance(handoff.get("latest_batch"), dict) else {}

    return {
        "queue_item_version": QUEUE_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_type": "sandbox_receipt_handoff",
        "source_path": str(handoff_path),
        "source_sha256": _sha256_file(handoff_path),
        "verification_path": str(verification_path),
        "verification_sha256": _sha256_file(verification_path),
        "verification_status": verification.get("status"),
        "queue_status": status,
        "handoff_verdict": verdict,
        "review_required": status == "QUEUED_FOR_REVIEW",
        "execution_authority": False,
        "install_authority": False,
        "allowed_actions": ["observe", "review", "classify"],
        "blocked_actions": ["install", "execute", "mutate_receiver", "dispatch_downstream_execution"],
        "constraints": sorted(set(handoff.get("constraints", [])) | {"cge_queue_is_non_executing", "review_before_action"}),
        "latest_batch": {
            "batch_number": latest_batch.get("batch_number"),
            "batch_sha256": latest_batch.get("batch_sha256"),
            "receipt_count": latest_batch.get("receipt_count"),
            "admitted_count": latest_batch.get("admitted_count"),
            "fail_closed_count": latest_batch.get("fail_closed_count"),
            "verification_status": latest_batch.get("verification_status"),
        },
    }


def build_queue(handoff_dir: Path, queue_dir: Path) -> dict[str, Any]:
    handoff_path = handoff_dir / "sandbox_receipt_handoff.json"
    verification_path = handoff_dir / "sandbox_receipt_handoff_verification.json"

    handoff = _load_json(handoff_path)
    verification = _load_json(verification_path)
    item = _make_queue_item(handoff, verification, handoff_path, verification_path)

    # This queue is a regenerated intake view over the latest verified handoff.
    # Do not retain stale regenerated items because their source hashes may no longer
    # match after upstream receipt/index/ledger artifacts are rebuilt.
    items = [item]

    queued_count = sum(1 for entry in items if entry.get("queue_status") == "QUEUED_FOR_REVIEW")
    observe_count = sum(1 for entry in items if entry.get("queue_status") == "OBSERVE_ONLY")
    blocked_count = sum(1 for entry in items if entry.get("queue_status") == "BLOCKED")

    return {
        "sandbox_receipt_queue_version": QUEUE_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "queue_scope": "CGE intake classification queue",
        "queue_mode": "latest_verified_handoff_view",
        "execution_authority": False,
        "install_authority": False,
        "item_count": len(items),
        "queued_for_review_count": queued_count,
        "observe_only_count": observe_count,
        "blocked_count": blocked_count,
        "latest_queue_item": item,
        "items": items,
    }


def write_queue(queue: dict[str, Any], queue_dir: Path) -> None:
    queue_dir.mkdir(parents=True, exist_ok=True)
    queue_path = queue_dir / "sandbox_receipt_queue.json"
    latest_path = queue_dir / "latest_queue_item.json"
    summary_path = queue_dir / "sandbox_receipt_queue.md"

    _write_json(queue_path, queue)
    _write_json(latest_path, queue.get("latest_queue_item", {}))

    latest = queue.get("latest_queue_item", {}) if isinstance(queue.get("latest_queue_item"), dict) else {}
    lines = [
        "# CGE Sandbox Receipt Intake Queue",
        "",
        f"- Queue version: `{queue['sandbox_receipt_queue_version']}`",
        f"- Generated: `{queue['generated_at_utc']}`",
        f"- Scope: `{queue['queue_scope']}`",
        f"- Mode: `{queue['queue_mode']}`",
        f"- Execution authority: `{queue['execution_authority']}`",
        f"- Install authority: `{queue['install_authority']}`",
        f"- Item count: `{queue['item_count']}`",
        f"- Queued for review: `{queue['queued_for_review_count']}`",
        f"- Observe only: `{queue['observe_only_count']}`",
        f"- Blocked: `{queue['blocked_count']}`",
        "",
        "## Latest Queue Item",
        "",
        f"- Queue status: `{latest.get('queue_status')}`",
        f"- Handoff verdict: `{latest.get('handoff_verdict')}`",
        f"- Review required: `{latest.get('review_required')}`",
        f"- Execution authority: `{latest.get('execution_authority')}`",
        f"- Install authority: `{latest.get('install_authority')}`",
        f"- Source SHA-256: `{latest.get('source_sha256')}`",
        "",
        "## Items",
        "",
        "| Created UTC | Status | Verdict | Review Required | Batch | Source SHA-256 |",
        "|---|---|---|---|---|---|",
    ]

    for entry in queue.get("items", []):
        batch = entry.get("latest_batch", {}) if isinstance(entry.get("latest_batch"), dict) else {}
        lines.append(
            "| {created} | {status} | {verdict} | {review} | {batch} | `{sha}` |".format(
                created=entry.get("created_at_utc"),
                status=entry.get("queue_status"),
                verdict=entry.get("handoff_verdict"),
                review=entry.get("review_required"),
                batch=batch.get("batch_number"),
                sha=entry.get("source_sha256"),
            )
        )

    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build non-executing CGE sandbox receipt intake queue")
    parser.add_argument("--handoff-dir", default=str(DEFAULT_HANDOFF_DIR))
    parser.add_argument("--queue-dir", default=str(DEFAULT_QUEUE_DIR))
    args = parser.parse_args()

    queue = build_queue(Path(args.handoff_dir), Path(args.queue_dir))
    write_queue(queue, Path(args.queue_dir))
    print(json.dumps(queue, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
