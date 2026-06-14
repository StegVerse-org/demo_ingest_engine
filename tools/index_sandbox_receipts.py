from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


INDEX_VERSION = "1.0"
DEFAULT_RECEIPTS_DIR = Path("reports/sandbox_receipts")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _iso_from_unix(value: Any) -> str | None:
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat().replace("+00:00", "Z")
    except Exception:
        return None


def _receipt_summary(path: Path, receipts_dir: Path) -> dict[str, Any]:
    try:
        data = _load_json(path)
    except Exception as exc:
        return {
            "path": str(path.relative_to(receipts_dir.parent)),
            "filename": path.name,
            "parseable": False,
            "error": f"{type(exc).__name__}: {exc}",
            "sha256": _sha256_file(path),
            "size_bytes": path.stat().st_size,
        }

    received_at_unix = data.get("received_at_unix")
    return {
        "path": str(path.relative_to(receipts_dir.parent)),
        "filename": path.name,
        "parseable": True,
        "schema": data.get("schema"),
        "verdict": data.get("verdict"),
        "admitted": data.get("admitted"),
        "sender_repository": data.get("sender_repository"),
        "receiver_repository": data.get("receiver_repository"),
        "requested_mode": data.get("requested_mode"),
        "credential_provider": data.get("credential_provider"),
        "policy_version": data.get("policy_version"),
        "policy_sha256": data.get("policy_sha256"),
        "packet_sha256": data.get("packet_sha256"),
        "received_at_unix": received_at_unix,
        "received_at_utc": _iso_from_unix(received_at_unix),
        "error_count": len(data.get("errors", [])) if isinstance(data.get("errors"), list) else None,
        "sha256": _sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def build_index(receipts_dir: Path) -> dict[str, Any]:
    receipts_dir.mkdir(parents=True, exist_ok=True)
    receipt_files = sorted(receipts_dir.glob("*.receipt.json"))
    items = [_receipt_summary(path, receipts_dir) for path in receipt_files]

    parseable_items = [item for item in items if item.get("parseable")]
    latest = None
    if parseable_items:
        latest = max(
            parseable_items,
            key=lambda item: item.get("received_at_unix") if item.get("received_at_unix") is not None else -1,
        )

    admitted_count = sum(1 for item in parseable_items if item.get("admitted") is True)
    fail_closed_count = sum(1 for item in parseable_items if item.get("verdict") == "FAIL_CLOSED")

    return {
        "sandbox_receipt_index_version": INDEX_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "receipts_dir": str(receipts_dir),
        "receipt_count": len(items),
        "parseable_count": len(parseable_items),
        "admitted_count": admitted_count,
        "fail_closed_count": fail_closed_count,
        "latest_receipt": latest,
        "receipts": items,
    }


def write_index(index: dict[str, Any], receipts_dir: Path) -> None:
    receipts_dir.mkdir(parents=True, exist_ok=True)

    index_json = receipts_dir / "sandbox_receipt_index.json"
    index_md = receipts_dir / "sandbox_receipt_index.md"
    latest_json = receipts_dir / "latest_sandbox_receipt.json"

    index_json.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")

    latest = index.get("latest_receipt")
    latest_json.write_text(json.dumps(latest or {}, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Sandbox Receipt Index",
        "",
        f"- Index version: `{index['sandbox_receipt_index_version']}`",
        f"- Generated: `{index['generated_at_utc']}`",
        f"- Receipt count: `{index['receipt_count']}`",
        f"- Parseable count: `{index['parseable_count']}`",
        f"- Admitted count: `{index['admitted_count']}`",
        f"- Fail-closed count: `{index['fail_closed_count']}`",
        "",
        "## Latest Receipt",
        "",
    ]

    if latest:
        lines.extend(
            [
                f"- Path: `{latest.get('path')}`",
                f"- Verdict: `{latest.get('verdict')}`",
                f"- Requested mode: `{latest.get('requested_mode')}`",
                f"- Sender: `{latest.get('sender_repository')}`",
                f"- Credential provider: `{latest.get('credential_provider')}`",
                f"- Policy SHA-256: `{latest.get('policy_sha256')}`",
                "",
            ]
        )
    else:
        lines.extend(["- none", ""])

    lines.extend(
        [
            "## Receipts",
            "",
            "| Received UTC | Verdict | Mode | Sender | Policy SHA-256 | File |",
            "|---|---|---|---|---|---|",
        ]
    )

    for item in sorted(index.get("receipts", []), key=lambda r: str(r.get("received_at_utc") or ""), reverse=True):
        lines.append(
            "| {received} | {verdict} | {mode} | {sender} | {policy} | `{path}` |".format(
                received=item.get("received_at_utc") or "unparseable",
                verdict=item.get("verdict") or "unknown",
                mode=item.get("requested_mode") or "unknown",
                sender=item.get("sender_repository") or "unknown",
                policy=item.get("policy_sha256") or "missing",
                path=item.get("path"),
            )
        )

    index_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build StegGhost sandbox receipt index")
    parser.add_argument(
        "--receipts-dir",
        default=str(DEFAULT_RECEIPTS_DIR),
        help="Directory containing *.receipt.json files",
    )
    args = parser.parse_args()

    receipts_dir = Path(args.receipts_dir)
    index = build_index(receipts_dir)
    write_index(index, receipts_dir)
    print(json.dumps(index, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
