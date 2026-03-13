from __future__ import annotations
from pathlib import Path
import json
import matplotlib.pyplot as plt

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def _bar_chart(labels, values, title: str, outpath: Path):
    if not labels:
        return
    plt.figure(figsize=(8, 5))
    plt.bar(labels, values)
    plt.title(title)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(outpath, dpi=160)
    plt.close()

def build_governance_visuals(reports_root: Path):
    reports_root.mkdir(parents=True, exist_ok=True)
    generated = []

    stress_path = reports_root / "stress_test_results.json"
    if stress_path.exists():
        stress = _load_json(stress_path)
        labels = ["allowed", "denied"]
        values = [stress.get("allowed_count", 0), stress.get("denied_count", 0)]
        out = reports_root / "stress_test_bar.png"
        _bar_chart(labels, values, "Governance Stress Test Outcomes", out)
        generated.append(out.name)

        zones = stress.get("denial_by_type", {})
        if zones:
            out2 = reports_root / "failure_zones_bar.png"
            _bar_chart(list(zones.keys()), list(zones.values()), "Failure Zones by Mutation Type", out2)
            generated.append(out2.name)

    phase_path = reports_root / "phase_diagram.json"
    if phase_path.exists():
        phase = _load_json(phase_path)
        counts = phase.get("region_counts", {})
        if counts:
            out = reports_root / "phase_regions_bar.png"
            _bar_chart(list(counts.keys()), list(counts.values()), "Governance Phase Regions", out)
            generated.append(out.name)

    recovery_path = reports_root / "recovery_metrics.json"
    if recovery_path.exists():
        rec = _load_json(recovery_path)
        labels = ["perturbed", "recovered"]
        values = [rec.get("perturbed_count", 0), rec.get("recovered_count", 0)]
        out = reports_root / "recovery_metrics_bar.png"
        _bar_chart(labels, values, "Recovery Metrics", out)
        generated.append(out.name)

    summary = {
        "visuals_version": "1.0",
        "generated_files": generated,
    }
    (reports_root / "visualization_manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary