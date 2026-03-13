from __future__ import annotations
from pathlib import Path
import hashlib
import json

def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def replay_event_log(reports_root: Path) -> dict:
    event_log_path = reports_root / "event_log.json"
    if not event_log_path.exists():
        return {
            "replay_version": "1.0",
            "status": "FAIL",
            "checks_passed": [],
            "checks_failed": ["event_log_missing"],
            "recomputed_event_chain_hash": None,
            "recorded_event_chain_hash": None,
        }

    event_log = _load_json(event_log_path)
    events = event_log.get("events", [])

    checks_passed = []
    checks_failed = []

    recomputed_events = []
    for event in events:
        payload = {
            "source": event["source"],
            "target": event["target"],
            "edge": event["edge"],
            "permitted": event["permitted"],
            "timestamp_utc": event["timestamp_utc"],
            "event_type": event["event_type"],
        }
        expected_event_id = _sha256_text(json.dumps(payload, sort_keys=True))[:16]
        if expected_event_id == event.get("event_id"):
            checks_passed.append(f"event_id_match:{event['event_id']}")
        else:
            checks_failed.append(f"event_id_mismatch:{event.get('event_id','missing')}")
        recomputed_events.append(payload)

    recomputed_chain_hash = _sha256_text(json.dumps(recomputed_events, sort_keys=True))
    recorded_chain_hash = event_log.get("event_chain_hash")

    if recorded_chain_hash is None:
        checks_failed.append("event_chain_hash_missing")
    elif recorded_chain_hash == recomputed_chain_hash:
        checks_passed.append("event_chain_hash_match")
    else:
        checks_failed.append("event_chain_hash_mismatch")

    return {
        "replay_version": "1.0",
        "status": "PASS" if not checks_failed else "FAIL",
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "recomputed_event_chain_hash": recomputed_chain_hash,
        "recorded_event_chain_hash": recorded_chain_hash,
        "event_count": len(events),
    }

def write_event_replay_reports(reports_root: Path, result: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "event_replay_verification.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )

    lines = [
        "# Event Replay Verification",
        "",
        f"- Status: **{result['status']}**",
        f"- Event count: `{result.get('event_count', 0)}`",
        f"- Checks passed: `{len(result['checks_passed'])}`",
        f"- Checks failed: `{len(result['checks_failed'])}`",
        "",
        "## Passed",
        "",
    ]
    for item in result["checks_passed"]:
        lines.append(f"- {item}")
    lines += ["", "## Failed", ""]
    for item in result["checks_failed"]:
        lines.append(f"- {item}")
    (reports_root / "event_replay_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")