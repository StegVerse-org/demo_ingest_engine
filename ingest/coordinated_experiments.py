from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

def build_coordinated_batch(mode: str, entities: list[str], batch_name: str, trials: int) -> dict:
    steps = []
    for idx, entity in enumerate(entities, start=1):
        steps.append({
            "step_id": f"coord_{idx:04d}",
            "entity": entity,
            "mode": mode,
            "order": idx,
            "action": "evaluate_then_record",
        })
    return {
        "batch_version": "1.0",
        "batch_name": batch_name,
        "mode": mode,
        "entity_count": len(entities),
        "trial_count": trials,
        "steps": steps,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

def write_coordinated_batch(reports_root: Path, batch: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "coordinated_experiment_batch.json").write_text(
        json.dumps(batch, indent=2), encoding="utf-8"
    )

    lines = [
        "# Coordinated Experiment Batch",
        "",
        f"- Batch: `{batch['batch_name']}`",
        f"- Mode: `{batch['mode']}`",
        f"- Entity count: `{batch['entity_count']}`",
        f"- Trial count: `{batch['trial_count']}`",
        "",
        "## Steps",
        "",
    ]
    for step in batch["steps"]:
        lines.append(f"- `{step['step_id']}` entity=`{step['entity']}` order=`{step['order']}` action=`{step['action']}`")
    (reports_root / "coordinated_experiment_batch.md").write_text("\n".join(lines) + "\n", encoding="utf-8")