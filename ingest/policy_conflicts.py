from __future__ import annotations
from pathlib import Path
import json

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def analyze_policy_conflicts(root: Path, entities: list[str]) -> dict:
    items = []
    by_pair = []
    verdicts = {}

    for entity in entities:
        reports_root = root / "entities" / entity / "reports"
        g = reports_root / "governance_receipt.json"
        a = reports_root / "admissibility_receipt.json"
        gu = reports_root / "guardian_receipt.json"

        verdicts[entity] = {
            "governance": _load_json(g).get("authorized") if g.exists() else None,
            "admissibility": _load_json(a).get("admissible") if a.exists() else None,
            "guardian": _load_json(gu).get("verdict") if gu.exists() else None,
        }

    for i, a in enumerate(entities):
        for b in entities[i+1:]:
            va = verdicts.get(a, {})
            vb = verdicts.get(b, {})
            conflict_fields = []
            for field in ["governance", "admissibility", "guardian"]:
                if va.get(field) != vb.get(field):
                    conflict_fields.append(field)
            by_pair.append({
                "pair": f"{a}<->{b}",
                "conflict": bool(conflict_fields),
                "fields": conflict_fields,
            })

    items = {
        "conflict_version": "1.0",
        "entities": entities,
        "verdicts": verdicts,
        "pairwise_conflicts": by_pair,
        "conflict_count": sum(1 for p in by_pair if p["conflict"]),
    }
    return items

def write_policy_conflict_reports(reports_root: Path, result: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "policy_conflicts.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Cross-Entity Policy Conflicts",
        "",
        f"- Conflict count: `{result['conflict_count']}`",
        "",
        "## Pairwise",
        "",
    ]
    for p in result["pairwise_conflicts"]:
        lines.append(f"- `{p['pair']}` conflict=`{p['conflict']}` fields=`{', '.join(p['fields']) if p['fields'] else 'none'}`")
    (reports_root / "policy_conflicts.md").write_text("\n".join(lines) + "\n", encoding="utf-8")