from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
import random

def load_adversarial_policy(path: Path) -> dict:
    if not path.exists():
        return {
            "policy_version": "1.0",
            "enabled": True,
            "seed": 42,
            "trial_count": 25,
            "candidate_modes": ["plan", "install"],
            "candidate_mutation_types": [
                "artifact_ingestion",
                "configuration_change",
                "documentation_change",
                "policy_change",
                "unknown_mutation"
            ]
        }
    return json.loads(path.read_text(encoding="utf-8"))

def generate_adversarial_trials(policy: dict) -> dict:
    seed = int(policy.get("seed", 42))
    random.seed(seed)
    modes = policy.get("candidate_modes", ["plan", "install"])
    muts = policy.get("candidate_mutation_types", ["unknown_mutation"])
    trial_count = max(1, int(policy.get("trial_count", 25)))

    trials = []
    for idx in range(trial_count):
        trials.append({
            "trial_id": f"adv_{idx+1:04d}",
            "mode": random.choice(modes),
            "mutation_type": random.choice(muts),
        })

    return {
        "adversarial_version": "1.0",
        "seed": seed,
        "trial_count": trial_count,
        "trials": trials,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

def evaluate_adversarial_trials(generated: dict, governance_policy: dict, admissibility_policy: dict, guardian_policy: dict) -> dict:
    results = []
    failure_zone_counts = {}
    for t in generated.get("trials", []):
        mode = t["mode"]
        mutation_type = t["mutation_type"]
        governance_allowed = mode in governance_policy.get("allowed_modes", []) and mutation_type in governance_policy.get("allowed_mutation_types", [])
        admissible = mutation_type in admissibility_policy.get("allowed_transitions", {}).get(mode, [])
        guardian_verdict = "guarded_allow" if mode in guardian_policy.get("execution_modes_touching_reality", []) else "allow"
        final_allowed = governance_allowed and admissible and guardian_verdict != "deny"
        result = {
            **t,
            "governance_allowed": governance_allowed,
            "admissible": admissible,
            "guardian_verdict": guardian_verdict,
            "final_allowed": final_allowed,
        }
        results.append(result)
        if not final_allowed:
            key = f"{mode}:{mutation_type}"
            failure_zone_counts[key] = failure_zone_counts.get(key, 0) + 1

    return {
        "evaluation_version": "1.0",
        "seed": generated.get("seed"),
        "trial_count": len(results),
        "results": results,
        "failure_zone_counts": failure_zone_counts,
        "timestamp_utc": generated.get("timestamp_utc"),
    }

def write_adversarial_reports(reports_root: Path, generated: dict, evaluated: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "adversarial_trials.json").write_text(json.dumps(generated, indent=2), encoding="utf-8")
    (reports_root / "adversarial_results.json").write_text(json.dumps(evaluated, indent=2), encoding="utf-8")