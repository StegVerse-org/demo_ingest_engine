from __future__ import annotations
from pathlib import Path
from datetime import datetime
import hashlib
import json

def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _latest_state_index(state_dir: Path) -> int:
    indices = []
    for p in state_dir.glob("state_*.json"):
        stem = p.stem
        try:
            indices.append(int(stem.split("_")[1]))
        except Exception:
            continue
    return max(indices) if indices else 0

def _load_previous_state(state_dir: Path, idx: int):
    if idx <= 0:
        return None
    p = state_dir / f"state_{idx:04d}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))

def append_state(reports_root: Path, receipt: dict, report: dict):
    state_dir = reports_root / "state_graph"
    state_dir.mkdir(parents=True, exist_ok=True)

    prev_idx = _latest_state_index(state_dir)
    prev_state = _load_previous_state(state_dir, prev_idx)

    prev_hash = prev_state["state_hash"] if prev_state else None
    next_idx = prev_idx + 1

    transition_material = json.dumps({
        "previous_state_hash": prev_hash,
        "receipt_hash": _sha256_text(json.dumps(receipt, sort_keys=True)),
        "report_hash": receipt["report_hash"],
        "mode": report.get("mode"),
        "source": report.get("source"),
    }, sort_keys=True)

    current_hash = _sha256_text(transition_material)

    state_record = {
        "state_version": "1.0",
        "state_id": f"state_{next_idx:04d}",
        "previous_state_id": prev_state["state_id"] if prev_state else None,
        "previous_state_hash": prev_hash,
        "mode": report.get("mode"),
        "source": report.get("source"),
        "report_hash": receipt["report_hash"],
        "bundle_hash": receipt["bundle_hash"],
        "receipt_hash": _sha256_text(json.dumps(receipt, sort_keys=True)),
        "state_hash": current_hash,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

    state_file = state_dir / f"{state_record['state_id']}.json"
    state_file.write_text(json.dumps(state_record, indent=2), encoding="utf-8")

    latest = {
        "latest_state_id": state_record["state_id"],
        "latest_state_hash": current_hash,
    }
    (state_dir / "latest_state.json").write_text(json.dumps(latest, indent=2), encoding="utf-8")

    lines = []
    for p in sorted(state_dir.glob("state_*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        lines.append(
            f"{data['state_id']} | prev={data.get('previous_state_id')} | hash={data['state_hash']} | mode={data['mode']}"
        )
    (state_dir / "state_chain.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    return state_record