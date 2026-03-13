from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

def load_stress_policy(path: Path) -> dict:
    if not path.exists():
        return {
            "policy_version": "1.0",
            "enabled": True,
            "trial_count": 12,
            "modes": ["plan", "install"],
            "mutation_types": [
                "artifact_ingestion",
                "configuration_change",
                "documentation_change",
                "policy_change",
                "unknown_mutation"
            ]
        }
    return json.loads(path.read_text(encoding="utf-8"))

def run_stress_trials(policy: dict, governance_policy: dict, admissibility_policy: dict, guardian_policy: dict) -> dict:
    trials = []
    modes = policy.get("modes", ["plan", "install"])
    mutation_types = policy.get("mutation_types", ["unknown_mutation"])
    requested_trials = max(1, int(policy.get("trial_count", len(modes) * len(mutation_types))))

    all_trials = []
    for mode in modes:
        for mutation_type in mutation_types:
            governance_allowed = (
                mode in governance_policy.get("allowed_modes", [])
                and mutation_type in governance_policy.get("allowed_mutation_types", [])
            )
            admissible = mutation_type in admissibility_policy.get("allowed_transitions", {}).get(mode, [])
            guardian_verdict = "guarded_allow" if mode in guardian_policy.get("execution_modes_touching_reality", []) else "allow"
            final_allowed = governance_allowed and admissible and guardian_verdict != "deny"

            all_trials.append({
                "mode": mode,
                "mutation_type": mutation_type,
                "governance_allowed": governance_allowed,
                "admissible": admissible,
                "guardian_verdict": guardian_verdict,
                "final_allowed": final_allowed,
            })

    trials = all_trials[:requested_trials]

    allowed_count = sum(1 for t in trials if t["final_allowed"])
    denied_count = len(trials) - allowed_count

    denial_by_type = {}
    for t in trials:
        if not t["final_allowed"]:
            denial_by_type[t["mutation_type"]] = denial_by_type.get(t["mutation_type"], 0) + 1

    return {
        "stress_test_version": "1.0",
        "trial_count": len(trials),
        "allowed_count": allowed_count,
        "denied_count": denied_count,
        "allow_rate": (allowed_count / len(trials)) if trials else 0.0,
        "deny_rate": (denied_count / len(trials)) if trials else 0.0,
        "denial_by_type": denial_by_type,
        "trials": trials,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

def write_stress_reports(reports_root: Path, result: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "stress_test_results.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )

    stability_map = {
        "stability_map_version": "1.0",
        "allow_rate": result["allow_rate"],
        "deny_rate": result["deny_rate"],
        "high_instability": result["deny_rate"] > 0.5,
        "timestamp_utc": result["timestamp_utc"],
    }
    (reports_root / "stability_map.json").write_text(
        json.dumps(stability_map, indent=2), encoding="utf-8"
    )

    failure_zones = {
        "failure_zone_version": "1.0",
        "denial_by_type": result["denial_by_type"],
        "dominant_failure_type": max(result["denial_by_type"], key=result["denial_by_type"].get) if result["denial_by_type"] else None,
        "timestamp_utc": result["timestamp_utc"],
    }
    (reports_root / "failure_zones.json").write_text(
        json.dumps(failure_zones, indent=2), encoding="utf-8"
    )

    lines = [
        "# Governance Stress Test Summary",
        "",
        f"- Trial count: `{result['trial_count']}`",
        f"- Allow rate: `{result['allow_rate']:.2f}`",
        f"- Deny rate: `{result['deny_rate']:.2f}`",
        "",
        "## Denial by Type",
        "",
    ]
    for k, v in sorted(result["denial_by_type"].items()):
        lines.append(f"- `{k}`: `{v}`")
    lines += ["", "## Trials", ""]
    for idx, t in enumerate(result["trials"], start=1):
        lines.append(
            f"- Trial {idx}: mode=`{t['mode']}` mutation=`{t['mutation_type']}` governance=`{t['governance_allowed']}` admissible=`{t['admissible']}` guardian=`{t['guardian_verdict']}` final=`{t['final_allowed']}`"
        )
    (reports_root / "stress_test_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")