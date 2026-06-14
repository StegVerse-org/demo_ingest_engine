from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERIFICATION_VERSION = "1.0"
DEFAULT_RECEIPTS_DIR = Path("reports/sandbox_receipts")


INDEX_FILENAMES = {
    "sandbox_receipt_index.json",
    "sandbox_receipt_index.md",
    "latest_sandbox_receipt.json",
    "sandbox_receipt_index_verification.json",
    "sandbox_receipt_index_verification.md",
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _receipt_files(receipts_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in receipts_dir.glob("*.receipt.json")
        if path.name not in INDEX_FILENAMES
    )


def verify_index(receipts_dir: Path) -> dict[str, Any]:
    checks_passed: list[str] = []
    checks_failed: list[str] = []

    index_path = receipts_dir / "sandbox_receipt_index.json"
    latest_path = receipts_dir / "latest_sandbox_receipt.json"
    summary_path = receipts_dir / "sandbox_receipt_index.md"

    if index_path.exists():
        checks_passed.append("index_json_exists")
        index = _load_json(index_path)
    else:
        checks_failed.append("index_json_missing")
        index = {}

    if latest_path.exists():
        checks_passed.append("latest_json_exists")
        latest = _load_json(latest_path)
    else:
        checks_failed.append("latest_json_missing")
        latest = {}

    if summary_path.exists():
        checks_passed.append("index_markdown_exists")
    else:
        checks_failed.append("index_markdown_missing")

    receipt_files = _receipt_files(receipts_dir)
    receipt_summaries = index.get("receipts", []) if isinstance(index.get("receipts"), list) else []

    if index.get("receipt_count") == len(receipt_files):
        checks_passed.append("receipt_count_matches_files")
    else:
        checks_failed.append(
            f"receipt_count_mismatch:index={index.get('receipt_count')} files={len(receipt_files)}"
        )

    indexed_by_filename = {
        item.get("filename"): item
        for item in receipt_summaries
        if isinstance(item, dict) and item.get("filename")
    }

    missing_from_index = []
    hash_mismatches = []
    parseable_count = 0
    admitted_count = 0
    fail_closed_count = 0

    for receipt_file in receipt_files:
        item = indexed_by_filename.get(receipt_file.name)
        if not item:
            missing_from_index.append(receipt_file.name)
            continue

        actual_hash = _sha256_file(receipt_file)
        if item.get("sha256") != actual_hash:
            hash_mismatches.append(receipt_file.name)

        try:
            data = _load_json(receipt_file)
            parseable_count += 1
            if data.get("admitted") is True:
                admitted_count += 1
            if data.get("verdict") == "FAIL_CLOSED":
                fail_closed_count += 1
        except Exception:
            pass

    if not missing_from_index:
        checks_passed.append("all_receipt_files_indexed")
    else:
        checks_failed.append(f"receipt_files_missing_from_index:{','.join(missing_from_index)}")

    if not hash_mismatches:
        checks_passed.append("receipt_hashes_match")
    else:
        checks_failed.append(f"receipt_hash_mismatch:{','.join(hash_mismatches)}")

    if index.get("parseable_count") == parseable_count:
        checks_passed.append("parseable_count_matches")
    else:
        checks_failed.append(
            f"parseable_count_mismatch:index={index.get('parseable_count')} recomputed={parseable_count}"
        )

    if index.get("admitted_count") == admitted_count:
        checks_passed.append("admitted_count_matches")
    else:
        checks_failed.append(
            f"admitted_count_mismatch:index={index.get('admitted_count')} recomputed={admitted_count}"
        )

    if index.get("fail_closed_count") == fail_closed_count:
        checks_passed.append("fail_closed_count_matches")
    else:
        checks_failed.append(
            f"fail_closed_count_mismatch:index={index.get('fail_closed_count')} recomputed={fail_closed_count}"
        )

    latest_index = index.get("latest_receipt") if isinstance(index.get("latest_receipt"), dict) else None
    if latest_index == latest:
        checks_passed.append("latest_json_matches_index")
    else:
        checks_failed.append("latest_json_mismatch")

    if latest_index:
        latest_filename = latest_index.get("filename")
        latest_file = receipts_dir / str(latest_filename)
        if latest_filename and latest_file.exists():
            checks_passed.append("latest_receipt_file_exists")
        else:
            checks_failed.append(f"latest_receipt_file_missing:{latest_filename}")
    elif receipt_files:
        checks_failed.append("latest_receipt_missing_despite_receipts")
    else:
        checks_passed.append("latest_receipt_empty_without_receipts")

    return {
        "sandbox_receipt_index_verification_version": VERIFICATION_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "receipts_dir": str(receipts_dir),
        "status": "PASS" if not checks_failed else "FAIL",
        "receipt_file_count": len(receipt_files),
        "indexed_receipt_count": len(receipt_summaries),
        "recomputed_parseable_count": parseable_count,
        "recomputed_admitted_count": admitted_count,
        "recomputed_fail_closed_count": fail_closed_count,
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
    }


def write_verification(result: dict[str, Any], receipts_dir: Path) -> None:
    receipts_dir.mkdir(parents=True, exist_ok=True)

    json_path = receipts_dir / "sandbox_receipt_index_verification.json"
    md_path = receipts_dir / "sandbox_receipt_index_verification.md"

    json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Sandbox Receipt Index Verification",
        "",
        f"- Verification version: `{result['sandbox_receipt_index_verification_version']}`",
        f"- Generated: `{result['generated_at_utc']}`",
        f"- Status: **{result['status']}**",
        f"- Receipt files: `{result['receipt_file_count']}`",
        f"- Indexed receipts: `{result['indexed_receipt_count']}`",
        f"- Recomputed parseable count: `{result['recomputed_parseable_count']}`",
        f"- Recomputed admitted count: `{result['recomputed_admitted_count']}`",
        f"- Recomputed fail-closed count: `{result['recomputed_fail_closed_count']}`",
        "",
        "## Passed",
        "",
    ]

    for item in result.get("checks_passed", []):
        lines.append(f"- `{item}`")

    lines.extend(["", "## Failed", ""])
    if result.get("checks_failed"):
        for item in result.get("checks_failed", []):
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay-verify StegGhost sandbox receipt index")
    parser.add_argument(
        "--receipts-dir",
        default=str(DEFAULT_RECEIPTS_DIR),
        help="Directory containing sandbox receipt index and *.receipt.json files",
    )
    args = parser.parse_args()

    receipts_dir = Path(args.receipts_dir)
    result = verify_index(receipts_dir)
    write_verification(result, receipts_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
