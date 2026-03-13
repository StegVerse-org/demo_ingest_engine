from __future__ import annotations
from pathlib import Path
import json

def write_state_graph_mermaid(reports_root: Path):
    state_dir = reports_root / "state_graph"
    state_dir.mkdir(parents=True, exist_ok=True)

    state_files = sorted(state_dir.glob("state_*.json"))
    nodes = []
    edges = []

    for state_file in state_files:
        data = json.loads(state_file.read_text(encoding="utf-8"))
        sid = data["state_id"]
        nodes.append(f'    {sid}["{sid}"]')
        prev = data.get("previous_state_id")
        if prev:
            edges.append(f"    {prev} --> {sid}")

    if not nodes:
        mermaid = "graph TD\n    empty[\"No states yet\"]\n"
    else:
        mermaid = "graph TD\n" + "\n".join(nodes + edges) + "\n"

    (state_dir / "state_graph.mmd").write_text(mermaid, encoding="utf-8")

    markdown = "# State Graph Visualization\n\n```mermaid\n" + mermaid + "```\n"
    (state_dir / "state_graph.md").write_text(markdown, encoding="utf-8")