from __future__ import annotations
from pathlib import Path
import json

def build_stability_heatmap(surface: dict, stress_results: dict | None = None) -> dict:
    matrix = {}
    for cell in surface.get("cells", []):
        mode = cell["mode"]
        mutation = cell["mutation_type"]
        score = 1.0 if cell["final_allowed"] else 0.0
        if cell["guardian_verdict"] == "guarded_allow":
            score = 0.5 if cell["final_allowed"] else 0.0
        matrix.setdefault(mode, {})[mutation] = score

    return {
        "heatmap_version": "1.0",
        "matrix": matrix,
        "stress_overlay": {
            "allow_rate": stress_results.get("allow_rate", 0.0),
            "deny_rate": stress_results.get("deny_rate", 0.0),
        } if stress_results else None,
    }

def write_heatmap_reports(reports_root: Path, heatmap: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "stability_heatmap.json").write_text(json.dumps(heatmap, indent=2), encoding="utf-8")

    lines = ["# Stability Heatmap", ""]
    for mode, row in heatmap["matrix"].items():
        lines.append(f"## {mode}")
        lines.append("")
        for mutation, score in sorted(row.items()):
            lines.append(f"- `{mutation}`: `{score}`")
        lines.append("")
    if heatmap.get("stress_overlay"):
        so = heatmap["stress_overlay"]
        lines += [
            "## Stress Overlay",
            "",
            f"- Allow rate: `{so['allow_rate']:.2f}`",
            f"- Deny rate: `{so['deny_rate']:.2f}`",
            ""
        ]
    (reports_root / "stability_heatmap.md").write_text("\n".join(lines), encoding="utf-8")