from __future__ import annotations
from pathlib import Path
import json

def build_policy_surface(governance_policy: dict, admissibility_policy: dict, guardian_policy: dict) -> dict:
    modes = sorted(set(governance_policy.get("allowed_modes", [])) | set(admissibility_policy.get("allowed_transitions", {}).keys()))
    mutation_types = sorted(set(governance_policy.get("allowed_mutation_types", [])) | {
        m for vals in admissibility_policy.get("allowed_transitions", {}).values() for m in vals
    })

    cells = []
    for mode in modes:
        for mutation_type in mutation_types:
            governance_allowed = mode in governance_policy.get("allowed_modes", []) and mutation_type in governance_policy.get("allowed_mutation_types", [])
            admissible = mutation_type in admissibility_policy.get("allowed_transitions", {}).get(mode, [])
            guardian_verdict = "guarded_allow" if mode in guardian_policy.get("execution_modes_touching_reality", []) else "allow"
            final_allowed = governance_allowed and admissible and guardian_verdict != "deny"

            cells.append({
                "mode": mode,
                "mutation_type": mutation_type,
                "governance_allowed": governance_allowed,
                "admissible": admissible,
                "guardian_verdict": guardian_verdict,
                "final_allowed": final_allowed,
            })

    return {
        "surface_version": "1.0",
        "modes": modes,
        "mutation_types": mutation_types,
        "cells": cells,
    }

def write_policy_surface_reports(reports_root: Path, surface: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "policy_surface.json").write_text(
        json.dumps(surface, indent=2), encoding="utf-8"
    )

    lines = [
        "# Governance Policy Surface",
        "",
        "| Mode | Mutation Type | Governance | Admissible | Guardian | Final |",
        "|---|---|---:|---:|---|---:|",
    ]
    for cell in surface["cells"]:
        lines.append(
            f"| {cell['mode']} | {cell['mutation_type']} | {cell['governance_allowed']} | {cell['admissible']} | {cell['guardian_verdict']} | {cell['final_allowed']} |"
        )
    (reports_root / "policy_surface.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    matrix = ["# Policy Surface Matrix", ""]
    for mode in surface["modes"]:
        matrix.append(f"## {mode}")
        matrix.append("")
        for mutation_type in surface["mutation_types"]:
            cell = next(c for c in surface["cells"] if c["mode"] == mode and c["mutation_type"] == mutation_type)
            mark = "ALLOW" if cell["final_allowed"] else "DENY"
            matrix.append(f"- `{mutation_type}` → `{mark}`")
        matrix.append("")
    (reports_root / "policy_surface_matrix.md").write_text("\n".join(matrix), encoding="utf-8")