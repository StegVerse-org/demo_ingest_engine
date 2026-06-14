from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RECEIPT_VERSION = "1.0"
DEFAULT_POLICY = Path("configs/stegghost_declared_task_policy.json")
DEFAULT_OUT_DIR = Path("manifest_receipts")


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


def validate_manifest(manifest: dict[str, Any], policy: dict[str, Any]) -> tuple[str, list[str], list[str]]:
    passed: list[str] = []
    failed: list[str] = []

    for field in policy.get("required_manifest_fields", []):
        if field in manifest:
            passed.append(f"required_field_present:{field}")
        else:
            failed.append(f"required_field_missing:{field}")

    if manifest.get("schema") == policy.get("allowed_schema"):
        passed.append("schema_allowed")
    else:
        failed.append(f"schema_not_allowed:{manifest.get('schema')}")

    if manifest.get("task_type") == policy.get("allowed_task_type"):
        passed.append("task_type_allowed")
    else:
        failed.append(f"task_type_not_allowed:{manifest.get('task_type')}")

    requested_mode = manifest.get("requested_mode")
    if requested_mode in policy.get("allowed_requested_modes", []):
        passed.append("requested_mode_allowed")
    else:
        failed.append(f"requested_mode_not_allowed:{requested_mode}")

    if requested_mode in policy.get("blocked_requested_modes", []):
        failed.append(f"requested_mode_blocked:{requested_mode}")
    else:
        passed.append("requested_mode_not_blocked")

    target = manifest.get("target", {}) if isinstance(manifest.get("target"), dict) else {}
    target_constraints = policy.get("target_constraints", {}) if isinstance(policy.get("target_constraints"), dict) else {}

    if target.get("recipient") == target_constraints.get("recipient"):
        passed.append("target_recipient_allowed")
    else:
        failed.append(f"target_recipient_not_allowed:{target.get('recipient')}")

    if target.get("sandbox_only") is True and target_constraints.get("sandbox_only") is True:
        passed.append("target_sandbox_only_true")
    else:
        failed.append("target_sandbox_only_not_true")

    boundary = manifest.get("boundary", {}) if isinstance(manifest.get("boundary"), dict) else {}
    boundary_constraints = policy.get("boundary_constraints", {}) if isinstance(policy.get("boundary_constraints"), dict) else {}

    for key, expected in boundary_constraints.items():
        actual = boundary.get(key)
        if actual is expected:
            passed.append(f"boundary_matches:{key}")
        else:
            failed.append(f"boundary_mismatch:{key}:expected={expected}:actual={actual}")

    test = manifest.get("test", {}) if isinstance(manifest.get("test"), dict) else {}
    if test.get("name") and test.get("input_ref"):
        passed.append("test_declaration_present")
    else:
        failed.append("test_declaration_missing_name_or_input_ref")

    verdict = "ADMISSIBLE_TEST_TASK" if not failed else "FAIL_CLOSED"
    return verdict, passed, failed


def build_receipt(manifest_path: Path, policy_path: Path, out_dir: Path) -> dict[str, Any]:
    manifest = _load_json(manifest_path)
    policy = _load_json(policy_path)
    verdict, checks_passed, checks_failed = validate_manifest(manifest, policy)

    return {
        "declared_task_manifest_receipt_version": RECEIPT_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "active_path": policy.get("active_path"),
        "submission_interfaces": policy.get("submission_interfaces"),
        "recipient": policy.get("recipient"),
        "manifest_path": str(manifest_path),
        "manifest_sha256": _sha256_file(manifest_path),
        "policy_path": str(policy_path),
        "policy_sha256": _sha256_file(policy_path),
        "schema": manifest.get("schema"),
        "task_type": manifest.get("task_type"),
        "requested_mode": manifest.get("requested_mode"),
        "submitter": manifest.get("submitter"),
        "target": manifest.get("target"),
        "test": manifest.get("test"),
        "verdict": verdict,
        "admissible": verdict == "ADMISSIBLE_TEST_TASK",
        "route_to_stegghost_ingestion": verdict == "ADMISSIBLE_TEST_TASK",
        "emit_result_receipt": verdict == "ADMISSIBLE_TEST_TASK",
        "return_result_to_submitter": verdict == "ADMISSIBLE_TEST_TASK",
        "execution_authority_outside_sandbox": False,
        "install_authority": False,
        "planning_authority": False,
        "conversation_loop_allowed": False,
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
    }


def write_receipt(receipt: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"declared_task_manifest_{_safe_timestamp()}.receipt.json"
    latest_path = out_dir / "latest_declared_task_manifest_receipt.json"
    md_path = out_dir / "latest_declared_task_manifest_receipt.md"

    _write_json(out_path, receipt)
    _write_json(latest_path, receipt)

    lines = [
        "# Declared Sandbox Test Task Manifest Receipt",
        "",
        f"- Verdict: **{receipt['verdict']}**",
        f"- Admissible: `{receipt['admissible']}`",
        f"- Route to StegGhost ingestion: `{receipt['route_to_stegghost_ingestion']}`",
        f"- Emit result receipt: `{receipt['emit_result_receipt']}`",
        f"- Return result to submitter: `{receipt['return_result_to_submitter']}`",
        f"- Install authority: `{receipt['install_authority']}`",
        f"- Execution authority outside sandbox: `{receipt['execution_authority_outside_sandbox']}`",
        f"- Planning authority: `{receipt['planning_authority']}`",
        f"- Conversation loop allowed: `{receipt['conversation_loop_allowed']}`",
        "",
        "## Failed Checks",
        "",
    ]
    if receipt.get("checks_failed"):
        for item in receipt["checks_failed"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Passed Checks", ""])
    for item in receipt.get("checks_passed", []):
        lines.append(f"- `{item}`")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate declared sandbox test task manifest and fail closed on all other manifests")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--receipt-path-file")
    args = parser.parse_args()

    receipt = build_receipt(Path(args.manifest), Path(args.policy), Path(args.out_dir))
    out_path = write_receipt(receipt, Path(args.out_dir))

    if args.receipt_path_file:
        Path(args.receipt_path_file).write_text(str(out_path), encoding="utf-8")

    print(json.dumps({"receipt_path": str(out_path), "receipt": receipt}, indent=2, sort_keys=True))
    return 0 if receipt.get("admissible") else 1


if __name__ == "__main__":
    raise SystemExit(main())
