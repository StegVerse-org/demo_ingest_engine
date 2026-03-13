from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
import hashlib

def _event_id(payload: dict) -> str:
    material = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(material).hexdigest()[:16]

def _chain_hash(events: list[dict]) -> str:
    normalized = []
    for event in events:
        normalized.append({
            "source": event["source"],
            "target": event["target"],
            "edge": event["edge"],
            "permitted": event["permitted"],
            "timestamp_utc": event["timestamp_utc"],
            "event_type": event["event_type"],
        })
    return hashlib.sha256(json.dumps(normalized, sort_keys=True).encode("utf-8")).hexdigest()

def emit_interaction_events(root: Path, entities: list[str], interaction_receipt: dict) -> dict:
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

    return {
        "event_bus_version": "1.1",
        "entities": entities,
        "event_count": len(events),
        "event_chain_hash": _chain_hash(events),
        "events": events,
    }

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
        f"- Event chain hash: `{event_log.get('event_chain_hash')}`",
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