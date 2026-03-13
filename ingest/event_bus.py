from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
import hashlib

def _event_id(payload: dict) -> str:
    material = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(material).hexdigest()[:16]

def emit_interaction_events(root: Path, entities: list[str], interaction_receipt: dict) -> dict:
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    events = []
    for edge in interaction_receipt.get("edges", []):
        payload = {
            "source": edge["source"],
            "target": edge["target"],
            "edge": edge["edge"],
            "permitted": edge["permitted"],
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "event_type": "INTERACTION_ALLOWED" if edge["permitted"] else "INTERACTION_BLOCKED",
        }
        payload["event_id"] = _event_id(payload)
        events.append(payload)

    event_log = {
        "event_bus_version": "1.0",
        "entities": entities,
        "event_count": len(events),
        "events": events,
    }
    return event_log

def write_event_bus_reports(root: Path, event_log: dict):
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    (reports_root / "event_log.json").write_text(
        json.dumps(event_log, indent=2), encoding="utf-8"
    )

    lines = [
        "# Event Bus Interaction Log",
        "",
        f"- Event count: `{event_log['event_count']}`",
        "",
        "## Events",
        "",
    ]
    for event in event_log["events"]:
        lines.extend([
            f"### {event['event_id']}",
            "",
            f"- Type: `{event['event_type']}`",
            f"- Source: `{event['source']}`",
            f"- Target: `{event['target']}`",
            f"- Edge: `{event['edge']}`",
            f"- Permitted: `{event['permitted']}`",
            "",
        ])
    (reports_root / "event_log.md").write_text("\n".join(lines), encoding="utf-8")