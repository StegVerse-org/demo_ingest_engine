from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERIFICATION_VERSION = "1.0"
DEFAULT_REVIEW_DIR = Path("review_receipts")
ALLOWED_VERDICTS = {"APPROVE_FOR_PLANNING", "HOLD_FOR_MORE_EVIDENCE", "REJECT"}


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


def verify_review(review_dir: Path) -> dict[str, Any]:
    checks_passed: list[str] = []
    checks_failed: list[str] = []

    latest_path = review_dir / "latest_sandbox_receipt_review.json"
    index_path = review_dir / "sandbox_receipt_review_index.json"
    index_md_path = review_dir / "sandbox_receipt_review_index.md"

    if latest_path.exists():
        checks_passed.append("latest_review_exists")
        latest = _load_json(latest_path)
    else:
        checks_failed.append("latest_review_missing")
        latest = {}

    if index_path.exists():
        checks_passed.append("review_index_exists")
        index = _load_json(index_path)
    else:
        checks_failed.append("review_index_missing")
        index = {}

    if index_md_path.exists():
        checks_passed.append("review_index_markdown_exists")
    else:
        checks_failed.append("review_index_markdown_missing")

    verdict = latest.get("verdict")
    if verdict in ALLOWED_VERDICTS:
        checks_passed.append("verdict_is_allowed")
    else:
        checks_failed.append(f"verdict_not_allowed:{verdict}")

    if latest.get("execution_authority") is False:
        checks_passed.append("execution_authority_false")
    else:
        checks_failed.append(f"execution_authority_not_false:{latest.get('execution_authority')}")

    if latest.get("install_authority") is False:
        checks_passed.append("install_authority_false")
    else:
        checks_failed.append(f"install_authority_not_false:{latest.get('install_authority')}")

    expected_planning = verdict == "APPROVE_FOR_PLANNING"
    if latest.get("planning_authority") is expected_planning:
        checks_passed.append("planning_authority_matches_verdict")
    else:
        checks_failed.append(f"planning_authority_mismatch:expected={expected_planning}:actual={latest.get('planning_authority')}")

    blocked = set(latest.get("blocked_actions", [])) if isinstance(latest.get("blocked_actions"), list) else set()
    if {"install", "execute"}.issubset(blocked):
        checks_passed.append("blocked_actions_include_install_execute")
    else:
        checks_failed.append("blocked_actions_missing_install_or_execute")

    queue_source = latest.get("queue_source", {}) if isinstance(latest.get("queue_source"), dict) else {}
    queue_path = Path(queue_source.get("path", "")) if queue_source.get("path") else None
    if queue_path and queue_path.exists() and _sha256_file(queue_path) == queue_source.get("sha256"):
        checks_passed.append("queue_source_hash_matches")
    else:
        checks_failed.append("queue_source_hash_mismatch")

    latest_queue_source = latest.get("latest_queue_item_source", {}) if isinstance(latest.get("latest_queue_item_source"), dict) else {}
    latest_queue_path = Path(latest_queue_source.get("path", "")) if latest_queue_source.get("path") else None
    if latest_queue_path and latest_queue_path.exists() and _sha256_file(latest_queue_path) == latest_queue_source.get("sha256"):
        checks_passed.append("latest_queue_item_source_hash_matches")
    else:
        checks_failed.append("latest_queue_item_source_hash_mismatch")

    queue_verification_source = latest.get("queue_verification_source", {}) if isinstance(latest.get("queue_verification_source"), dict) else {}
    queue_verification_path = Path(queue_verification_source.get("path", "")) if queue_verification_source.get("path") else None
    if queue_verification_path and queue_verification_path.exists() and _sha256_file(queue_verification_path) == queue_verification_source.get("sha256"):
        checks_passed.append("queue_verification_source_hash_matches")
    else:
        checks_failed.append("queue_verification_source_hash_mismatch")

    if queue_verification_source.get("status") == "PASS":
        checks_passed.append("queue_verification_status_pass")
    else:
        checks_failed.append(f"queue_verification_status_not_pass:{queue_verification_source.get('status')}")

    reviews = index.get("reviews", []) if isinstance(index.get("reviews"), list) else []
    if index.get("review_count") == len(reviews):
        checks_passed.append("review_count_matches")
    else:
        checks_failed.append("review_count_mismatch")

    latest_sha = _sha256_file(latest_path) if latest_path.exists() else None
    latest_index = index.get("latest_review", {}) if isinstance(index.get("latest_review"), dict) else {}
    if latest_sha and latest_index.get("sha256") == latest_sha:
        checks_passed.append("latest_index_hash_matches_latest_review")
    else:
        checks_failed.append("latest_index_hash_mismatch")

    return {
        "sandbox_receipt_review_verification_version": VERIFICATION_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "review_dir": str(review_dir),
        "status": "PASS" if not checks_failed else "FAIL",
        "verdict": verdict,
        "reviewer": latest.get("reviewer"),
        "execution_authority": latest.get("execution_authority"),
        "install_authority": latest.get("install_authority"),
        "planning_authority": latest.get("planning_authority"),
        "review_count": index.get("review_count"),
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
    }


def write_verification(result: dict[str, Any], review_dir: Path) -> None:
    json_path = review_dir / "sandbox_receipt_review_verification.json"
    md_path = review_dir / "sandbox_receipt_review_verification.md"

    _write_json(json_path, result)

    lines = [
        "# Sandbox Receipt Review Verification",
        "",
        f"- Version: `{result['sandbox_receipt_review_verification_version']}`",
        f"- Generated: `{result['generated_at_utc']}`",
        f"- Status: **{result['status']}**",
        f"- Verdict: `{result.get('verdict')}`",
        f"- Reviewer: `{result.get('reviewer')}`",
        f"- Execution authority: `{result.get('execution_authority')}`",
        f"- Install authority: `{result.get('install_authority')}`",
        f"- Planning authority: `{result.get('planning_authority')}`",
        f"- Review count: `{result.get('review_count')}`",
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
    parser = argparse.ArgumentParser(description="Verify latest sandbox receipt human review receipt")
    parser.add_argument("--review-dir", default=str(DEFAULT_REVIEW_DIR))
    args = parser.parse_args()

    result = verify_review(Path(args.review_dir))
    write_verification(result, Path(args.review_dir))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
