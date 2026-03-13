from __future__ import annotations
from pathlib import Path
import json

def build_phase_diagram(surface: dict, stress_results: dict | None = None) -> dict:
    regions = []
    for cell in surface.get("cells", []):
        if cell["final_allowed"] and cell["guardian_verdict"] == "allow":
            region = "stable_allow"
        elif cell["final_allowed"] and cell["guardian_verdict"] == "guarded_allow":
            region = "guarded_execution"
        elif (not cell["governance_allowed"]) or (not cell["admissible"]):
            region = "inadmissible"
        else:
            region = "blocked"
        regions.append({
            "mode": cell["mode"],
            "mutation_type": cell["mutation_type"],
            "region": region,
            "governance_allowed": cell["governance_allowed"],
            "admissible": cell["admissible"],
            "guardian_verdict": cell["guardian_verdict"],
            "final_allowed": cell["final_allowed"],
        })

    counts = {}
    for r in regions:
        counts[r["region"]] = counts.get(r["region"], 0) + 1

    stress_overlay = None
    if stress_results:
        stress_overlay = {
            "trial_count": stress_results.get("trial_count", 0),
            "allow_rate": stress_results.get("allow_rate", 0.0),
            "deny_rate": stress_results.get("deny_rate", 0.0),
            "high_instability": stress_results.get("deny_rate", 0.0) > 0.5,
        }

    return {
        "phase_diagram_version": "1.0",
        "region_counts": counts,
        "regions": regions,
        "stress_overlay": stress_overlay,
    }

def write_phase_reports(reports_root: Path, phase: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "phase_diagram.json").write_text(
        json.dumps(phase, indent=2), encoding="utf-8"
    )

    lines = [
        "# Governance Phase Diagram",
        "",
        "## Region Counts",
        "",
    ]
    for k, v in sorted(phase["region_counts"].items()):
        lines.append(f"- `{k}`: `{v}`")

    if phase.get("stress_overlay"):
        so = phase["stress_overlay"]
        lines += [
            "",
            "## Stress Overlay",
            "",
            f"- Trial count: `{so['trial_count']}`",
            f"- Allow rate: `{so['allow_rate']:.2f}`",
            f"- Deny rate: `{so['deny_rate']:.2f}`",
            f"- High instability: `{so['high_instability']}`",
        ]

    lines += ["", "## Regions", "", "| Mode | Mutation Type | Region | Final |", "|---|---|---|---:|"]
    for r in phase["regions"]:
        lines.append(f"| {r['mode']} | {r['mutation_type']} | {r['region']} | {r['final_allowed']} |")
    (reports_root / "phase_diagram.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    mermaid = ["graph TD"]
    added = set()
    for r in phase["regions"]:
        mode_node = f"mode_{r['mode']}"
        mut_node = f"mut_{r['mutation_type']}"
        reg_node = f"reg_{r['region']}"
        if mode_node not in added:
            mermaid.append(f'    {mode_node}["mode: {r["mode"]}"]')
            added.add(mode_node)
        if mut_node not in added:
            mermaid.append(f'    {mut_node}["mutation: {r["mutation_type"]}"]')
            added.add(mut_node)
        if reg_node not in added:
            mermaid.append(f'    {reg_node}["region: {r["region"]}"]')
            added.add(reg_node)
        mermaid.append(f"    {mode_node} --> {mut_node}")
        mermaid.append(f"    {mut_node} --> {reg_node}")
    mermaid_text = "\n".join(mermaid) + "\n"
    (reports_root / "phase_diagram.mmd").write_text(mermaid_text, encoding="utf-8")
    (reports_root / "phase_diagram_mermaid.md").write_text(
        "# Governance Phase Diagram Mermaid\n\n```mermaid\n" + mermaid_text + "```\n",
        encoding="utf-8"
    )