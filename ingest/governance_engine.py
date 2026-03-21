from __future__ import annotations

from pathlib import Path
from datetime import datetime
import hashlib
import json


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_policy(path: Path) -> dict:
    if not path.exists():
        return {
            "policy_version": "1.0",
            "allowed_modes": ["plan", "install"],
            "deny_missing_source": True,
            "allowed_roots": ["incoming", "staging", "reports"],
            "blocked_suffixes": [".exe", ".dll", ".so"],
            "allowed_mutation_types": [
                "artifact_ingestion",
                "configuration_change",
                "documentation_change",
                "policy_change",
                "unknown_mutation",
            ],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_policy_context(policy: dict, entity: str, mode: str) -> dict:
    """
    Supports both:
    - legacy flat policy format
    - entity-aware policy format (v1.1+)
    """
    allowed_roots = policy.get("allowed_roots", ["incoming", "staging", "reports"])
    blocked_suffixes = policy.get("blocked_suffixes", [".exe", ".dll", ".so"])
    deny_missing_source = policy.get("deny_missing_source", True)

    if "entities" in policy:
        entity_policy = policy.get("entities", {}).get(entity, {})
        mode_rules = entity_policy.get("mode_rules", {})
        mode_rule = mode_rules.get(mode, {})

        return {
            "allowed_modes": entity_policy.get("allowed_modes", policy.get("allowed_modes", [])),
            "allowed_mutation_types": mode_rule.get("allowed_mutations", []),
            "blocked_mutation_types": mode_rule.get("blocked_mutations", []),
            "allowed_roots": allowed_roots,
            "blocked_suffixes": blocked_suffixes,
            "deny_missing_source": deny_missing_source,
        }

    return {
        "allowed_modes": policy.get("allowed_modes", []),
        "allowed_mutation_types": policy.get("allowed_mutation_types", []),
        "blocked_mutation_types": [],
        "allowed_roots": allowed_roots,
        "blocked_suffixes": blocked_suffixes,
        "deny_missing_source": deny_missing_source,
    }


def evaluate_mutation(
    source: Path,
    mode: str,
    policy: dict,
    mutation_type: str | None = None,
    entity: str = "default",
) -> dict:
    checks: list[str] = []
    failures: list[str] = []

    ctx = _resolve_policy_context(policy, entity=entity, mode=mode)

    if mode in ctx["allowed_modes"]:
        checks.append("mode_allowed")
    else:
        failures.append("mode_not_allowed")

    if source.exists():
        checks.append("source_exists")
    else:
        if ctx["deny_missing_source"]:
            failures.append("source_missing")

    source_str = str(source)
    allowed_roots = ctx["allowed_roots"]
    if any(root in source_str for root in allowed_roots):
        checks.append("source_root_allowed")
    else:
        failures.append("source_root_not_allowed")

    blocked_suffixes = ctx["blocked_suffixes"]
    if source.is_file() and source.suffix.lower() in blocked_suffixes:
        failures.append("blocked_suffix")
    else:
        checks.append("suffix_allowed")

    allowed_mutation_types = ctx["allowed_mutation_types"]
    blocked_mutation_types = ctx["blocked_mutation_types"]

    if mutation_type is None:
        checks.append("mutation_type_allowed")
    elif mutation_type in blocked_mutation_types:
        failures.append("mutation_type_blocked")
    elif mutation_type in allowed_mutation_types:
        checks.append("mutation_type_allowed")
    else:
        failures.append("mutation_type_not_allowed")

    authorized = len(failures) == 0

    receipt = {
        "receipt_version": "1.1",
        "policy_version": policy.get("policy_version", "unknown"),
        "mode": mode,
        "source": source_str,
        "mutation_type": mutation_type,
        "authorized": authorized,
        "checks_passed": checks,
        "checks_failed": failures,
        "policy_hash": _sha256_text(json.dumps(policy, sort_keys=True)),
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "entity": entity,
    }
    return receipt


def write_governance_receipt(reports_root: Path, receipt: dict) -> None:
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "governance_receipt.json").write_text(
        json.dumps(receipt, indent=2),
        encoding="utf-8",
    )
    (reports_root / "policy_hash.txt").write_text(
        receipt["policy_hash"] + "\n",
        encoding="utf-8",
    )
