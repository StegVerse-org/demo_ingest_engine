from __future__ import annotations
from pathlib import Path
import json

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def compute_recovery_metrics(root: Path, entities: list[str]) -> dict:
    total = len(entities)
    recovered = 0
    perturbed = 0
    details = []

    for entity in entities:
        reports_root = root / "entities" / entity / "reports"
        rec = reports_root / "recovery_receipt.json"
        per = reports_root / "perturbation_receipt.json"
        rec_data = _load_json(rec) if rec.exists() else {}
        per_data = _load_json(per) if per.exists() else {}

        if per_data.get("perturbation_enabled"):
            perturbed += 1
        if rec_data.get("recovered"):
            recovered += 1

        details.append({
            "entity": entity,
            "perturbed": bool(per_data.get("perturbation_enabled")),
            "recovered": bool(rec_data.get("recovered")),
        })

    return {
        "recovery_metrics_version": "1.0",
        "entity_count": total,
        "perturbed_count": perturbed,
        "recovered_count": recovered,
        "recovery_rate": (recovered / perturbed) if perturbed else 0.0,
        "details": details,
    }

def write_recovery_metrics_reports(reports_root: Path, result: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "recovery_metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Recovery Metrics",
        "",
        f"- Entity count: `{result['entity_count']}`",
        f"- Perturbed count: `{result['perturbed_count']}`",
        f"- Recovered count: `{result['recovered_count']}`",
        f"- Recovery rate: `{result['recovery_rate']:.2f}`",
        "",
    ]
    for d in result["details"]:
        lines.append(f"- `{d['entity']}` perturbed=`{d['perturbed']}` recovered=`{d['recovered']}`")
    (reports_root / "recovery_metrics.md").write_text("\n".join(lines) + "\n", encoding="utf-8")