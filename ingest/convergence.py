from __future__ import annotations
from pathlib import Path
import json

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def analyze_convergence(root: Path, entity_names: list[str]) -> dict:
    replay_statuses = {}
    state_hashes = {}
    latest_states = {}

    for entity in entity_names:
        reports_root = root / "entities" / entity / "reports"
        replay_path = reports_root / "replay_verification.json"
        state_hash_path = reports_root / "state_hash.txt"
        latest_state_path = reports_root / "state_graph" / "latest_state.json"

        if replay_path.exists():
            replay_statuses[entity] = _load_json(replay_path).get("status")
        if state_hash_path.exists():
            state_hashes[entity] = state_hash_path.read_text(encoding="utf-8").strip()
        if latest_state_path.exists():
            latest_states[entity] = _load_json(latest_state_path).get("latest_state_id")

    unique_replay = sorted(set(v for v in replay_statuses.values() if v is not None))
    unique_hashes = sorted(set(v for v in state_hashes.values() if v is not None))
    unique_latest = sorted(set(v for v in latest_states.values() if v is not None))

    result = {
        "convergence_version": "1.0",
        "entities": entity_names,
        "replay_statuses": replay_statuses,
        "state_hashes": state_hashes,
        "latest_states": latest_states,
        "replay_converged": len(unique_replay) <= 1,
        "state_hash_converged": len(unique_hashes) <= 1,
        "latest_state_converged": len(unique_latest) <= 1,
        "overall_converged": len(unique_replay) <= 1 and len(unique_hashes) <= 1 and len(unique_latest) <= 1,
    }
    return result

def write_convergence_reports(root: Path, result: dict):
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    (reports_root / "cross_entity_replay_convergence.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )

    lines = [
        "# Cross-Entity Replay Convergence",
        "",
        f"- Replay converged: `{result['replay_converged']}`",
        f"- State hash converged: `{result['state_hash_converged']}`",
        f"- Latest state converged: `{result['latest_state_converged']}`",
        f"- Overall converged: `{result['overall_converged']}`",
        "",
        "## Entities",
        "",
    ]
    for entity in result["entities"]:
        lines.extend([
            f"### {entity}",
            "",
            f"- Replay status: `{result['replay_statuses'].get(entity, 'missing')}`",
            f"- State hash: `{result['state_hashes'].get(entity, 'missing')}`",
            f"- Latest state: `{result['latest_states'].get(entity, 'missing')}`",
            "",
        ])
    (reports_root / "cross_entity_replay_convergence.md").write_text("\n".join(lines), encoding="utf-8")