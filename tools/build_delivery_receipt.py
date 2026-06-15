from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "1.0"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build(intake_path: Path) -> dict[str, Any]:
    intake = load_json(intake_path)
    if intake.get("verdict") != "ACCEPTED_FOR_DELIVERY" or intake.get("accepted") is not True:
        raise ValueError("accepted result intake receipt required")

    return {
        "delivery_receipt_version": VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "intake_path": str(intake_path),
        "intake_sha256": sha256_file(intake_path),
        "result_ref": intake.get("result_receipt_path"),
        "result_sha256": intake.get("result_receipt_sha256"),
        "submitter": intake.get("submitter"),
        "test": intake.get("test"),
        "delivery_status": "READY_FOR_SUBMITTER",
        "bounded_result_only": True,
        "return_to_submitter": True,
    }


def write(receipt: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"delivery_{stamp()}.receipt.json"
    latest_path = out_dir / "latest_delivery_receipt.json"
    md_path = out_dir / "latest_delivery_receipt.md"

    write_json(out_path, receipt)
    write_json(latest_path, receipt)
    md_path.write_text(
        "\n".join([
            "# Delivery Receipt",
            "",
            f"- Delivery status: `{receipt.get('delivery_status')}`",
            f"- Bounded result only: `{receipt.get('bounded_result_only')}`",
            f"- Return to submitter: `{receipt.get('return_to_submitter')}`",
            f"- Result SHA-256: `{receipt.get('result_sha256')}`",
        ]) + "\n",
        encoding="utf-8",
    )
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build delivery receipt from accepted result intake")
    parser.add_argument("--intake", required=True)
    parser.add_argument("--out-dir", default="result_delivery")
    parser.add_argument("--delivery-path-file")
    args = parser.parse_args()

    receipt = build(Path(args.intake))
    out_path = write(receipt, Path(args.out_dir))
    if args.delivery_path_file:
        Path(args.delivery_path_file).write_text(str(out_path), encoding="utf-8")
    print(json.dumps({"delivery_receipt_path": str(out_path), "delivery_receipt": receipt}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
