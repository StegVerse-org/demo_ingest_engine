from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REVIEW_RECEIPT_VERSION = "1.0"
DEFAULT_QUEUE_DIR = Path("cge_intake")
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


def _safe_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_review_receipt(
    queue_dir: Path,
    reviewer: str,
    verdict: str,
    rationale: str,
    review_scope: str,
) -> dict[str, Any]:
    if verdict not in ALLOWED_VERDICTS:
        raise ValueError(f"verdict must be one of {sorted(ALLOWED_VERDICTS)}")

    queue_path = queue_dir / "sandbox_receipt_queue.json"
    latest_item_path = queue_dir / "latest_queue_item.json"
    queue_verification_path = queue_dir / "sandbox_receipt_queue_verification.json"

    queue = _load_json(queue_path)
    latest_item = _load_json(latest_item_path)
    queue_verification = _load_json(queue_verification_path)

    if queue_verification.get("status") != "PASS":
        raise ValueError("queue verification must be PASS before review receipt can be generated")

    if latest_item.get("execution_authority") is not False or latest_item.get("install_authority") is not False:
        raise ValueError("latest queue item must not carry execution or install authority")

    return {
        "sandbox_receipt_review_version": REVIEW_RECEIPT_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "reviewer": reviewer,
        "review_scope": review_scope,
        "verdict": verdict,
        "rationale": rationale,
        "execution_authority": False,
        "install_authority": False,
        "planning_authority": verdict == "APPROVE_FOR_PLANNING",
        "allowed_next_steps": ["planning_packet"] if verdict == "APPROVE_FOR_PLANNING" else ["observe", "request_more_evidence"],
        "blocked_actions": ["install", "execute", "mutate_receiver", "dispatch_downstream_execution"],
        "queue_source": {
            "path": str(queue_path),
            "sha256": _sha256_file(queue_path),
            "item_count": queue.get("item_count"),
            "queued_for_review_count": queue.get("queued_for_review_count"),
        },
        "latest_queue_item_source": {
            "path": str(latest_item_path),
            "sha256": _sha256_file(latest_item_path),
            "queue_status": latest_item.get("queue_status"),
            "handoff_verdict": latest_item.get("handoff_verdict"),
            "review_required": latest_item.get("review_required"),
            "source_sha256": latest_item.get("source_sha256"),
        },
        "queue_verification_source": {
            "path": str(queue_verification_path),
            "sha256": _sha256_file(queue_verification_path),
            "status": queue_verification.get("status"),
        },
    }


def write_review_receipt(receipt: dict[str, Any], review_dir: Path) -> Path:
    review_dir.mkdir(parents=True, exist_ok=True)
    out_path = review_dir / f"sandbox_receipt_review_{_safe_timestamp()}.json"
    latest_path = review_dir / "latest_sandbox_receipt_review.json"
    index_path = review_dir / "sandbox_receipt_review_index.json"
    md_path = review_dir / "sandbox_receipt_review_index.md"

    _write_json(out_path, receipt)
    _write_json(latest_path, receipt)

    existing: list[dict[str, Any]] = []
    if index_path.exists():
        try:
            previous = _load_json(index_path)
            if isinstance(previous.get("reviews"), list):
                existing = previous["reviews"]
        except Exception:
            existing = []

    summary = {
        "path": str(out_path),
        "sha256": _sha256_file(out_path),
        "created_at_utc": receipt.get("created_at_utc"),
        "reviewer": receipt.get("reviewer"),
        "verdict": receipt.get("verdict"),
        "execution_authority": receipt.get("execution_authority"),
        "install_authority": receipt.get("install_authority"),
        "planning_authority": receipt.get("planning_authority"),
    }

    known = {item.get("sha256") for item in existing if isinstance(item, dict)}
    if summary["sha256"] not in known:
        existing.append(summary)

    index = {
        "sandbox_receipt_review_index_version": REVIEW_RECEIPT_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "review_count": len(existing),
        "latest_review": summary,
        "reviews": existing,
    }
    _write_json(index_path, index)

    lines = [
        "# Sandbox Receipt Review Index",
        "",
        f"- Review count: `{index['review_count']}`",
        f"- Latest verdict: `{summary['verdict']}`",
        f"- Latest reviewer: `{summary['reviewer']}`",
        f"- Execution authority: `{summary['execution_authority']}`",
        f"- Install authority: `{summary['install_authority']}`",
        f"- Planning authority: `{summary['planning_authority']}`",
        "",
        "## Reviews",
        "",
        "| Created UTC | Verdict | Reviewer | Planning | File |",
        "|---|---|---|---|---|",
    ]

    for item in existing:
        lines.append(
            "| {created} | {verdict} | {reviewer} | {planning} | `{path}` |".format(
                created=item.get("created_at_utc"),
                verdict=item.get("verdict"),
                reviewer=item.get("reviewer"),
                planning=item.get("planning_authority"),
                path=item.get("path"),
            )
        )

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create manual human review receipt for verified sandbox queue item")
    parser.add_argument("--queue-dir", default=str(DEFAULT_QUEUE_DIR))
    parser.add_argument("--review-dir", default=str(DEFAULT_REVIEW_DIR))
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--verdict", required=True, choices=sorted(ALLOWED_VERDICTS))
    parser.add_argument("--rationale", required=True)
    parser.add_argument("--review-scope", default="sandbox_receipt_queue_latest_item")
    args = parser.parse_args()

    receipt = build_review_receipt(
        queue_dir=Path(args.queue_dir),
        reviewer=args.reviewer,
        verdict=args.verdict,
        rationale=args.rationale,
        review_scope=args.review_scope,
    )
    out_path = write_review_receipt(receipt, Path(args.review_dir))
    print(json.dumps({"review_receipt_path": str(out_path), "review_receipt": receipt}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
