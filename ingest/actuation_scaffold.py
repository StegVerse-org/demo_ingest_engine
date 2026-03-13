from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

def load_actuation_policy(path: Path) -> dict:
    if not path.exists():
        return {
            "policy_version": "1.0",
            "enabled": False,
            "allowed_targets": [],
            "mode": "artifact_only"
        }
    return json.loads(path.read_text(encoding="utf-8"))

def build_actuation_plan(source: Path, entities: list[str], policy: dict) -> dict:
    actions = []
    for entity in entities:
        actions.append({
            "entity": entity,
            "target": str(source),
            "allowed": bool(policy.get("enabled", False)) and str(source) in set(policy.get("allowed_targets", [])),
            "mode": policy.get("mode", "artifact_only"),
        })
    return {
        "actuation_plan_version": "1.0",
        "enabled": bool(policy.get("enabled", False)),
        "actions": actions,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

def write_actuation_reports(reports_root: Path, plan: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "actuation_plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")

    lines = [
        "# Actuation Scaffold",
        "",
        f"- Enabled: `{plan['enabled']}`",
        "",
    ]
    for action in plan["actions"]:
        lines.append(f"- entity=`{action['entity']}` target=`{action['target']}` allowed=`{action['allowed']}` mode=`{action['mode']}`")
    (reports_root / "actuation_plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")