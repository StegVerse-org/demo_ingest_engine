from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

def run_governance_experiment(root: Path, entity_results: list[dict], trials: int) -> dict:
    authorized = sum(1 for r in entity_results if r.get("allowed"))
    denied = len(entity_results) - authorized
    verification_pass = sum(1 for r in entity_results if r.get("verification_status") == "PASS")
    replay_pass = sum(1 for r in entity_results if r.get("replay_status") == "PASS")

    experiment = {
        "experiment_version": "1.0",
        "trial_count": trials,
        "entity_count": len(entity_results),
        "authorized_count": authorized,
        "denied_count": denied,
        "verification_pass_count": verification_pass,
        "replay_pass_count": replay_pass,
        "authorization_rate": (authorized / len(entity_results)) if entity_results else 0.0,
        "verification_rate": (verification_pass / len(entity_results)) if entity_results else 0.0,
        "replay_rate": (replay_pass / len(entity_results)) if entity_results else 0.0,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "results": entity_results,
    }
    return experiment

def write_experiment_reports(root: Path, experiment: dict):
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "experiment_results.json").write_text(json.dumps(experiment, indent=2), encoding="utf-8")

    stability = {
        "stability_metrics_version": "1.0",
        "authorization_rate": experiment["authorization_rate"],
        "verification_rate": experiment["verification_rate"],
        "replay_rate": experiment["replay_rate"],
        "system_stable": experiment["verification_rate"] == 1.0 and experiment["replay_rate"] == 1.0,
        "timestamp_utc": experiment["timestamp_utc"],
    }
    (reports_root / "stability_metrics.json").write_text(json.dumps(stability, indent=2), encoding="utf-8")

    divergence = {
        "divergence_statistics_version": "1.0",
        "authorized_count": experiment["authorized_count"],
        "denied_count": experiment["denied_count"],
        "denial_fraction": (experiment["denied_count"] / experiment["entity_count"]) if experiment["entity_count"] else 0.0,
        "timestamp_utc": experiment["timestamp_utc"],
    }
    (reports_root / "divergence_statistics.json").write_text(json.dumps(divergence, indent=2), encoding="utf-8")