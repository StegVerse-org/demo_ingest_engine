from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

def load_interaction_policy(root: Path) -> dict:
    path = root / "configs" / "interaction_policy.json"
    if not path.exists():
        return {
            "policy_version": "1.0",
            "default_mode": "isolated",
            "allowed_edges": [],
            "blocked_edges": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))

def _edge_key(a: str, b: str) -> str:
    return f"{a}->{b}"

def evaluate_interactions(root: Path, entities: list[str]) -> dict:
    policy = load_interaction_policy(root)
    default_mode = policy.get("default_mode", "isolated")
    allowed = set(policy.get("allowed_edges", []))
    blocked = set(policy.get("blocked_edges", []))

    edges = []
    for src in entities:
        for dst in entities:
            if src == dst:
                continue
            key = _edge_key(src, dst)
            permitted = False
            if key in blocked:
                permitted = False
            elif key in allowed:
                permitted = True
            elif default_mode == "open":
                permitted = True
            else:
                permitted = False
            edges.append({
                "source": src,
                "target": dst,
                "edge": key,
                "permitted": permitted,
            })

    return {
        "receipt_version": "1.0",
        "policy_version": policy.get("policy_version", "unknown"),
        "default_mode": default_mode,
        "entities": entities,
        "edges": edges,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

def write_interaction_reports(root: Path, receipt: dict):
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    (reports_root / "interaction_receipt.json").write_text(
        json.dumps(receipt, indent=2), encoding="utf-8"
    )

    lines = [
        "# Cross-Entity Interaction Policy",
        "",
        f"- Policy version: `{receipt['policy_version']}`",
        f"- Default mode: `{receipt['default_mode']}`",
        "",
        "## Edges",
        "",
    ]
    for edge in receipt["edges"]:
        lines.append(
            f"- `{edge['edge']}` → `{'allowed' if edge['permitted'] else 'blocked'}`"
        )
    (reports_root / "interaction_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    mermaid_lines = ["graph TD"]
    for entity in receipt["entities"]:
        mermaid_lines.append(f"    {entity}[\"{entity}\"]")
    for edge in receipt["edges"]:
        if edge["permitted"]:
            mermaid_lines.append(f"    {edge['source']} --> {edge['target']}")
    mermaid = "\n".join(mermaid_lines) + "\n"
    (reports_root / "interaction_graph.mmd").write_text(mermaid, encoding="utf-8")
    (reports_root / "interaction_graph.md").write_text(
        "# Interaction Graph\n\n```mermaid\n" + mermaid + "```\n",
        encoding="utf-8"
    )