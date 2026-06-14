from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERIFICATION_VERSION = "1.0"
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


def verify_queue(queue_dir: Path) -> dict[str, Any]:
    checks_passed: list[str] = []
    checks_failed: list[str] = []

    queue_path = queue_dir / "sandbox_receipt_queue.json"
    latest_path = queue_dir / "latest_queue_item.json"
    summary_path = queue_dir / "sandbox_receipt_queue.md"

    if queue_path.exists():
        checks_passed.append("queue_json_exists")
        queue = _load_json(queue_path)
    else:
        checks_failed.append("queue_json_missing")
        queue = {}

    if latest_path.exists():
        checks_passed.append("latest_queue_item_exists")
        latest = _load_json(latest_path)
    else:
        checks_failed.append("latest_queue_item_missing")
        latest = {}

    if summary_path.exists():
        checks_passed.append("queue_markdown_exists")
    else:
        checks_failed.append("queue_markdown_missing")

    if queue.get("execution_authority") is False:
        checks_passed.append("queue_execution_authority_false")
    else:
        checks_failed.append(f"queue_execution_authority_not_false:{queue.get('execution_authority')}")

    if queue.get("install_authority") is False:
        checks_passed.append("queue_install_authority_false")
    else:
        checks_failed.append(f"queue_install_authority_not_false:{queue.get('install_authority')}")

    items = queue.get("items", []) if isinstance(queue.get("items"), list) else []
    if queue.get("item_count") == len(items):
        checks_passed.append("item_count_matches")
    else:
        checks_failed.append(f"item_count_mismatch:index={queue.get('item_count')} actual={len(items)}")

    if queue.get("latest_queue_item") == latest:
        checks_passed.append("latest_queue_item_matches_queue")
    else:
        checks_failed.append("latest_queue_item_mismatch")

    blocked_required = {"install", "execute"}
    allowed_required = {"observe", "review", "classify"}
    bad_items: list[str] = []
    source_hash_mismatches: list[str] = []

    for idx, item in enumerate(items):
        label = f"item_{idx}"
        if item.get("execution_authority") is not False:
            bad_items.append(f"{label}:execution_authority")
        if item.get("install_authority") is not False:
            bad_items.append(f"{label}:install_authority")

        blocked = set(item.get("blocked_actions", [])) if isinstance(item.get("blocked_actions"), list) else set()
        allowed = set(item.get("allowed_actions", [])) if isinstance(item.get("allowed_actions"), list) else set()

        if not blocked_required.issubset(blocked):
            bad_items.append(f"{label}:blocked_actions_missing:{','.join(sorted(blocked_required - blocked))}")
        if not allowed_required.issubset(allowed):
            bad_items.append(f"{label}:allowed_actions_missing:{','.join(sorted(allowed_required - allowed))}")
        if blocked.intersection({"observe", "review", "classify"}):
            bad_items.append(f"{label}:blocked_review_actions")
        if allowed.intersection({"install", "execute", "mutate_receiver", "dispatch_downstream_execution"}):
            bad_items.append(f"{label}:allowed_execution_actions")

        source_path = item.get("source_path")
        source_sha = item.get("source_sha256")
        if source_path and Path(source_path).exists():
            actual = _sha256_file(Path(source_path))
            if source_sha != actual:
                source_hash_mismatches.append(label)
        else:
            bad_items.append(f"{label}:source_missing:{source_path}")

    if not bad_items:
        checks_passed.append("all_items_are_non_executing_review_records")
    else:
        checks_failed.append(f"bad_queue_items:{';'.join(bad_items)}")

    if not source_hash_mismatches:
        checks_passed.append("item_source_hashes_match")
    else:
        checks_failed.append(f"item_source_hash_mismatches:{','.join(source_hash_mismatches)}")

    queued_count = sum(1 for item in items if item.get("queue_status") == "QUEUED_FOR_REVIEW")
    observe_count = sum(1 for item in items if item.get("queue_status") == "OBSERVE_ONLY")
    blocked_count = sum(1 for item in items if item.get("queue_status") == "BLOCKED")

    if queue.get("queued_for_review_count") == queued_count:
        checks_passed.append("queued_for_review_count_matches")
    else:
        checks_failed.append("queued_for_review_count_mismatch")

    if queue.get("observe_only_count") == observe_count:
        checks_passed.append("observe_only_count_matches")
    else:
        checks_failed.append("observe_only_count_mismatch")

    if queue.get("blocked_count") == blocked_count:
        checks_passed.append("blocked_count_matches")
    else:
        checks_failed.append("blocked_count_mismatch")

    return {
        "sandbox_receipt_queue_verification_version": VERIFICATION_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "queue_dir": str(queue_dir),
        "status": "PASS" if not checks_failed else "FAIL",
        "item_count": len(items),
        "queued_for_review_count": queued_count,
        "observe_only_count": observe_count,
        "blocked_count": blocked_count,
        "execution_authority": queue.get("execution_authority"),
        "install_authority": queue.get("install_authority"),
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
    }


def write_verification(result: dict[str, Any], queue_dir: Path) -> None:
    json_path = queue_dir / "sandbox_receipt_queue_verification.json"
    md_path = queue_dir / "sandbox_receipt_queue_verification.md"

    _write_json(json_path, result)

    lines = [
        "# CGE Sandbox Receipt Queue Verification",
        "",
        f"- Version: `{result['sandbox_receipt_queue_verification_version']}`",
        f"- Generated: `{result['generated_at_utc']}`",
        f"- Status: **{result['status']}**",
        f"- Item count: `{result['item_count']}`",
        f"- Queued for review: `{result['queued_for_review_count']}`",
        f"- Observe only: `{result['observe_only_count']}`",
        f"- Blocked: `{result['blocked_count']}`",
        f"- Execution authority: `{result.get('execution_authority')}`",
        f"- Install authority: `{result.get('install_authority')}`",
        "",
        "## Failed Checks",
        "",
    ]

    if result.get("checks_failed"):
        for item in result["checks_failed"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Passed Checks", ""])
    for item in result.get("checks_passed", []):
        lines.append(f"- `{item}`")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify non-executing CGE sandbox receipt queue")
    parser.add_argument("--queue-dir", default=str(DEFAULT_QUEUE_DIR))
    args = parser.parse_args()

    result = verify_queue(Path(args.queue_dir))
    write_verification(result, Path(args.queue_dir))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
