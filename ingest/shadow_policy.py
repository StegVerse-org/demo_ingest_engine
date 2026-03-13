from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

def load_shadow_policy(path: Path) -> dict:
    if not path.exists():
        return {
            "policy_version": "1.0",
            "enabled": True,
            "scenarios": [
                {
                    "name": "strict_install",
                    "override_mode": "install",
                    "deny_mutation_types": ["unknown_mutation", "policy_change"],
                    "label": "Stricter install boundary"
                },
                {
                    "name": "lenient_plan",
                    "override_mode": "plan",
                    "allow_all_mutation_types": True,
                    "label": "Lenient observational mode"
                }
            ]
        }
    return json.loads(path.read_text(encoding="utf-8"))

def evaluate_shadow_scenarios(mode: str, mutation_type: str, governance_receipt: dict, admissibility_receipt: dict, guardian_receipt: dict, policy: dict) -> dict:
    scenarios = []
    if not policy.get("enabled", True):
        return {
            "receipt_version": "1.0",
            "enabled": False,
            "mode": mode,
            "mutation_type": mutation_type,
            "scenario_count": 0,
            "scenarios": [],
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        }

    for scenario in policy.get("scenarios", []):
        scenario_mode = scenario.get("override_mode", mode)
        deny_types = set(scenario.get("deny_mutation_types", []))
        allow_all = bool(scenario.get("allow_all_mutation_types", False))

        governance_authorized = governance_receipt.get("authorized", False)
        admissible = admissibility_receipt.get("admissible", False)
        guardian_verdict = guardian_receipt.get("verdict", "deny")

        counterfactual_allowed = governance_authorized and admissible and guardian_verdict != "deny"
        reasons = []

        if mutation_type in deny_types:
            counterfactual_allowed = False
            reasons.append("shadow_denied_mutation_type")

        if allow_all:
            reasons.append("shadow_allow_all_mutation_types")

        if scenario_mode != mode:
            reasons.append(f"mode_override:{mode}->{scenario_mode}")

        scenarios.append({
            "name": scenario.get("name", "unnamed"),
            "label": scenario.get("label", ""),
            "scenario_mode": scenario_mode,
            "counterfactual_allowed": counterfactual_allowed,
            "reasons": reasons,
        })

    return {
        "receipt_version": "1.0",
        "enabled": True,
        "mode": mode,
        "mutation_type": mutation_type,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

def write_shadow_reports(reports_root: Path, receipt: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "shadow_policy_receipt.json").write_text(
        json.dumps(receipt, indent=2), encoding="utf-8"
    )

    lines = [
        "# Shadow Policy Counterfactuals",
        "",
        f"- Enabled: `{receipt['enabled']}`",
        f"- Scenario count: `{receipt['scenario_count']}`",
        "",
        "## Scenarios",
        "",
    ]
    for scenario in receipt.get("scenarios", []):
        lines.extend([
            f"### {scenario['name']}",
            "",
            f"- Label: `{scenario['label']}`",
            f"- Scenario mode: `{scenario['scenario_mode']}`",
            f"- Counterfactual allowed: `{scenario['counterfactual_allowed']}`",
            f"- Reasons: `{', '.join(scenario['reasons']) if scenario['reasons'] else 'none'}`",
            "",
        ])
    (reports_root / "shadow_policy_summary.md").write_text("\n".join(lines), encoding="utf-8")