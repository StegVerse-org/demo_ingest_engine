from __future__ import annotations
from pathlib import Path
import json

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def compare_entities(root: Path, entity_names: list[str]) -> dict:
    comparisons = []
    state_hashes = {}
    mutation_types = {}
    governance_statuses = {}

    for entity in entity_names:
        reports_root = root / "entities" / entity / "reports"
        state_hash_path = reports_root / "state_hash.txt"
        mutation_path = reports_root / "mutation_receipt.json"
        governance_path = reports_root / "governance_receipt.json"

        if state_hash_path.exists():
            state_hashes[entity] = state_hash_path.read_text(encoding="utf-8").strip()
        if mutation_path.exists():
            mutation_types[entity] = _load_json(mutation_path).get("mutation_type")
        if governance_path.exists():
            governance_statuses[entity] = _load_json(governance_path).get("authorized")

    unique_hashes = sorted(set(state_hashes.values()))
    unique_mutations = sorted(set(v for v in mutation_types.values() if v is not None))
    unique_governance = sorted(set(v for v in governance_statuses.values() if v is not None))

    divergence = {
        "divergence_version": "1.0",
        "entities": entity_names,
        "state_hashes": state_hashes,
        "mutation_types": mutation_types,
        "governance_statuses": governance_statuses,
        "state_hash_diverged": len(unique_hashes) > 1,
        "mutation_type_diverged": len(unique_mutations) > 1,
        "governance_diverged": len(unique_governance) > 1,
    }
    return divergence

def write_comparison_reports(root: Path, divergence: dict):
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    (reports_root / "cross_entity_comparison.json").write_text(
        json.dumps(divergence, indent=2), encoding="utf-8"
    )

    lines = [
        "# Cross-Entity Comparison",
        "",
        f"- State hash diverged: `{divergence['state_hash_diverged']}`",
        f"- Mutation type diverged: `{divergence['mutation_type_diverged']}`",
        f"- Governance diverged: `{divergence['governance_diverged']}`",
        "",
        "## Entities",
        "",
    ]
    for entity in divergence["entities"]:
        lines.extend([
            f"### {entity}",
            "",
            f"- State hash: `{divergence['state_hashes'].get(entity, 'missing')}`",
            f"- Mutation type: `{divergence['mutation_types'].get(entity, 'missing')}`",
            f"- Governance authorized: `{divergence['governance_statuses'].get(entity, 'missing')}`",
            "",
        ])
    (reports_root / "cross_entity_summary.md").write_text("\n".join(lines), encoding="utf-8")