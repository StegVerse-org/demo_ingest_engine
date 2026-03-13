from __future__ import annotations
from pathlib import Path
import json

def write_paper_ready_reports(reports_root: Path, stress_results: dict | None, phase_diagram: dict | None, surface: dict | None, adversarial_eval: dict | None):
    reports_root.mkdir(parents=True, exist_ok=True)

    summary = {
        "paper_metrics_version": "1.0",
        "stress_trial_count": stress_results.get("trial_count", 0) if stress_results else 0,
        "stress_allow_rate": stress_results.get("allow_rate", 0.0) if stress_results else 0.0,
        "stress_deny_rate": stress_results.get("deny_rate", 0.0) if stress_results else 0.0,
        "phase_region_counts": phase_diagram.get("region_counts", {}) if phase_diagram else {},
        "surface_cell_count": len(surface.get("cells", [])) if surface else 0,
        "adversarial_failure_zones": adversarial_eval.get("failure_zone_counts", {}) if adversarial_eval else {},
    }
    (reports_root / "paper_metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# Paper-Ready Governance Metrics",
        "",
        f"- Stress trial count: `{summary['stress_trial_count']}`",
        f"- Stress allow rate: `{summary['stress_allow_rate']:.2f}`",
        f"- Stress deny rate: `{summary['stress_deny_rate']:.2f}`",
        f"- Policy surface cells: `{summary['surface_cell_count']}`",
        "",
        "## Phase Regions",
        "",
    ]
    for k, v in sorted(summary["phase_region_counts"].items()):
        lines.append(f"- `{k}`: `{v}`")
    lines += ["", "## Adversarial Failure Zones", ""]
    for k, v in sorted(summary["adversarial_failure_zones"].items()):
        lines.append(f"- `{k}`: `{v}`")
    (reports_root / "paper_metrics_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")