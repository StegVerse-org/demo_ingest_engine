from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


DEFAULT_POLICY_PATH = Path("configs/tvc_bridge_policy.json")
EXPECTED_SCHEMA = "stegverse.entity_sandbox_bridge.v1"
EXPECTED_EVENT_TYPE = "entity_sandbox_receipt"
EXPECTED_TRANSPORT_ACTION = "repository_dispatch"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _packet_hash(packet: Any) -> str:
    payload = json.dumps(packet, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _policy_hash(policy: dict[str, Any]) -> str:
    payload = json.dumps(policy, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _policy_error(field: str, expected: Any, actual: Any) -> dict[str, Any]:
    return {
        "field": field,
        "expected": expected,
        "actual": actual,
        "source": "configs/tvc_bridge_policy.json",
    }


def validate_policy(policy: Any) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []

    if not isinstance(policy, dict):
        return [
            _policy_error(
                "policy",
                "object",
                type(policy).__name__,
            )
        ]

    required_top_level = [
        "policy_version",
        "credential_provider",
        "sender_repository",
        "receiver_repository",
        "allowed_event_types",
        "allowed_requested_modes",
        "blocked_requested_modes",
        "allowed_transport_actions",
        "credential_constraints",
        "receiver_enforcement",
    ]

    for key in required_top_level:
        if key not in policy:
            errors.append(_policy_error(key, "present", None))

    if policy.get("credential_provider") != "TV/TVC":
        errors.append(_policy_error("credential_provider", "TV/TVC", policy.get("credential_provider")))

    if EXPECTED_EVENT_TYPE not in set(policy.get("allowed_event_types", [])):
        errors.append(
            _policy_error(
                "allowed_event_types",
                f"contains:{EXPECTED_EVENT_TYPE}",
                policy.get("allowed_event_types"),
            )
        )

    if EXPECTED_TRANSPORT_ACTION not in set(policy.get("allowed_transport_actions", [])):
        errors.append(
            _policy_error(
                "allowed_transport_actions",
                f"contains:{EXPECTED_TRANSPORT_ACTION}",
                policy.get("allowed_transport_actions"),
            )
        )

    blocked_modes = set(policy.get("blocked_requested_modes", []))
    if "install" not in blocked_modes:
        errors.append(_policy_error("blocked_requested_modes", "contains:install", policy.get("blocked_requested_modes")))

    constraints = policy.get("credential_constraints", {})
    if not isinstance(constraints, dict):
        errors.append(_policy_error("credential_constraints", "object", type(constraints).__name__))
        constraints = {}

    required_constraints = {
        "long_lived_repo_secret_allowed": False,
        "ephemeral_token_required": True,
        "token_scope_must_be_receiver_only": True,
        "token_must_not_grant_contents_write_to_sender": True,
        "token_must_not_grant_org_admin": True,
    }

    for key, expected in required_constraints.items():
        actual = constraints.get(key)
        if actual is not expected:
            errors.append(_policy_error(f"credential_constraints.{key}", expected, actual))

    enforcement = policy.get("receiver_enforcement", {})
    if not isinstance(enforcement, dict):
        errors.append(_policy_error("receiver_enforcement", "object", type(enforcement).__name__))
        enforcement = {}

    required_enforcement = {
        "validate_packet_schema": True,
        "validate_sender_repository": True,
        "validate_receiver_repository": True,
        "fail_closed_on_install_request": True,
        "record_admission_receipt": True,
    }

    for key, expected in required_enforcement.items():
        actual = enforcement.get(key)
        if actual is not expected:
            errors.append(_policy_error(f"receiver_enforcement.{key}", expected, actual))

    return errors


def validate_packet(packet: Any, policy: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []

    if not isinstance(packet, dict):
        return [
            {
                "field": "packet",
                "expected": "object",
                "actual": type(packet).__name__,
                "source": "received_packet",
            }
        ]

    if packet.get("schema") != EXPECTED_SCHEMA:
        errors.append(
            {
                "field": "schema",
                "expected": EXPECTED_SCHEMA,
                "actual": packet.get("schema"),
                "source": "received_packet",
            }
        )

    sender_repository = policy.get("sender_repository")
    receiver_repository = policy.get("receiver_repository")

    if packet.get("sender_repository") != sender_repository:
        errors.append(
            {
                "field": "sender_repository",
                "expected": sender_repository,
                "actual": packet.get("sender_repository"),
                "source": "configs/tvc_bridge_policy.json",
            }
        )

    if packet.get("receiver_repository") != receiver_repository:
        errors.append(
            {
                "field": "receiver_repository",
                "expected": receiver_repository,
                "actual": packet.get("receiver_repository"),
                "source": "configs/tvc_bridge_policy.json",
            }
        )

    event_type = packet.get("event_type", EXPECTED_EVENT_TYPE)
    if event_type not in set(policy.get("allowed_event_types", [])):
        errors.append(
            {
                "field": "event_type",
                "expected": sorted(policy.get("allowed_event_types", [])),
                "actual": event_type,
                "source": "configs/tvc_bridge_policy.json",
            }
        )

    requested_mode = packet.get("requested_mode", "review")
    allowed_modes = set(policy.get("allowed_requested_modes", []))
    blocked_modes = set(policy.get("blocked_requested_modes", []))

    if requested_mode in blocked_modes:
        errors.append(
            {
                "field": "requested_mode",
                "expected": f"not in blocked_requested_modes:{sorted(blocked_modes)}",
                "actual": requested_mode,
                "source": "configs/tvc_bridge_policy.json",
            }
        )

    if requested_mode not in allowed_modes:
        errors.append(
            {
                "field": "requested_mode",
                "expected": sorted(allowed_modes),
                "actual": requested_mode,
                "source": "configs/tvc_bridge_policy.json",
            }
        )

    boundary = packet.get("boundary", {})
    if not isinstance(boundary, dict):
        errors.append(
            {
                "field": "boundary",
                "expected": "object",
                "actual": type(boundary).__name__,
                "source": "received_packet",
            }
        )
        boundary = {}

    if boundary.get("sender_may_install_into_receiver") is not False:
        errors.append(
            {
                "field": "boundary.sender_may_install_into_receiver",
                "expected": False,
                "actual": boundary.get("sender_may_install_into_receiver"),
                "source": "received_packet",
            }
        )

    if boundary.get("receiver_must_fail_closed_on_install_request") is not True:
        errors.append(
            {
                "field": "boundary.receiver_must_fail_closed_on_install_request",
                "expected": True,
                "actual": boundary.get("receiver_must_fail_closed_on_install_request"),
                "source": "received_packet",
            }
        )

    return errors


def build_receipt(packet: Any, policy: dict[str, Any], errors: list[dict[str, Any]]) -> dict[str, Any]:
    requested_mode = packet.get("requested_mode", "review") if isinstance(packet, dict) else None

    return {
        "schema": "stegverse.org_sandbox_receipt_admission.v1",
        "received_at_unix": time.time(),
        "receiver_repository": policy.get("receiver_repository"),
        "sender_repository": packet.get("sender_repository") if isinstance(packet, dict) else None,
        "credential_provider": policy.get("credential_provider"),
        "policy_version": policy.get("policy_version"),
        "policy_sha256": _policy_hash(policy),
        "requested_mode": requested_mode,
        "admitted": len(errors) == 0,
        "verdict": "RECEIVED_FOR_REVIEW" if len(errors) == 0 else "FAIL_CLOSED",
        "errors": errors,
        "packet_sha256": _packet_hash(packet),
        "packet": packet,
    }


def write_receipt(receipt: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_ts = str(int(receipt["received_at_unix"] * 1000))
    out_path = out_dir / f"stegghost_{safe_ts}.receipt.json"
    out_path.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate StegGhost sandbox bridge packet")
    parser.add_argument("--packet", required=True, help="Path to bridge packet JSON")
    parser.add_argument(
        "--policy",
        default=str(DEFAULT_POLICY_PATH),
        help="Path to TV/TVC bridge policy JSON",
    )
    parser.add_argument(
        "--out-dir",
        default="reports/sandbox_receipts",
        help="Directory where admission receipt should be written",
    )
    parser.add_argument(
        "--receipt-path-file",
        default="receipt_path.txt",
        help="Path where the generated receipt path should be written",
    )
    args = parser.parse_args()

    packet = _load_json(Path(args.packet))
    policy = _load_json(Path(args.policy))

    errors = validate_policy(policy)
    if not errors:
        errors.extend(validate_packet(packet, policy))

    receipt = build_receipt(packet, policy if isinstance(policy, dict) else {}, errors)
    receipt_path = write_receipt(receipt, Path(args.out_dir))

    Path(args.receipt_path_file).write_text(str(receipt_path), encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
