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


def build_intake(result_path: Path) -> dict[str, Any]:
    result = load_json(result_path)
    failures: list[str] = []
    passed: list[str] = []

    if result.get("bounded_result_only") is True:
        passed.append("bounded_result_only_true")
    else:
        failures.append("bounded_result_only_not_true")

    if result.get("ready_for_return") is True:
        passed.append("ready_for_return_true")
    else:
        failures.append("ready_for_return_not_true")

    if result.get("return_to_submitter") is True:
        passed.append("return_to_submitter_true")
    else:
        failures.append("return_to_submitter_not_true")

    if result.get("intake_receipt_sha256"):
        passed.append("intake_receipt_hash_present")
    else:
        failures.append("intake_receipt_hash_missing")

    accepted = not failures
    return {
        "stegghost_result_intake_version": VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "result_receipt_path": str(result_path),
        "result_receipt_sha256": sha256_file(result_path),
        "result_status": result.get("result_status"),
        "test": result.get("test"),
        "submitter": result.get("submitter"),
        "accepted": accepted,
        "verdict": "ACCEPTED_FOR_DELIVERY" if accepted else "FAIL_CLOSED",
        "delivery_allowed": accepted,
        "bounded_result_only": result.get("bounded_result_only") is True,
        "ready_for_return": result.get("ready_for_return") is True,
        "return_to_submitter": result.get("return_to_submitter") is True,
        "checks_passed": passed,
        "checks_failed": failures,
    }


def write_intake(receipt: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"stegghost_result_intake_{stamp()}.receipt.json"
    latest_path = out_dir / "latest_stegghost_result_intake_receipt.json"
    md_path = out_dir / "latest_stegghost_result_intake_receipt.md"

    write_json(out_path, receipt)
    write_json(latest_path, receipt)

    lines = [
        "# StegGhost Result Intake Receipt",
        "",
        f"- Verdict: **{receipt.get('verdict')}**",
        f"- Accepted: `{receipt.get('accepted')}`",
        f"- Delivery allowed: `{receipt.get('delivery_allowed')}`",
        f"- Bounded result only: `{receipt.get('bounded_result_only')}`",
        f"- Ready for return: `{receipt.get('ready_for_return')}`",
        f"- Return to submitter: `{receipt.get('return_to_submitter')}`",
        "",
        "## Failed Checks",
        "",
    ]
    if receipt.get("checks_failed"):
        for item in receipt["checks_failed"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Intake StegGhost bounded result receipt")
    parser.add_argument("--result", required=True)
    parser.add_argument("--out-dir", default="result_intake")
    parser.add_argument("--intake-path-file")
    args = parser.parse_args()

    receipt = build_intake(Path(args.result))
    out_path = write_intake(receipt, Path(args.out_dir))
    if args.intake_path_file:
        Path(args.intake_path_file).write_text(str(out_path), encoding="utf-8")
    print(json.dumps({"intake_receipt_path": str(out_path), "intake_receipt": receipt}, indent=2, sort_keys=True))
    return 0 if receipt.get("accepted") else 1


if __name__ == "__main__":
    raise SystemExit(main())
