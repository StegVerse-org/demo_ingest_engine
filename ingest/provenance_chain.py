from __future__ import annotations
from pathlib import Path
from datetime import datetime
import hashlib
import json

def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def append_provenance_step(root: Path) -> dict:
    reports_root = root / "reports"
    prov_dir = reports_root / "provenance_chain"
    prov_dir.mkdir(parents=True, exist_ok=True)

    existing = sorted(prov_dir.glob("provenance_step_*.json"))
    prev = _load_json(existing[-1]) if existing else None

    prev_id = prev["step_id"] if prev else None
    prev_hash = prev["provenance_hash"] if prev else None
    next_idx = len(existing) + 1

    state_hash = None
    state_hash_path = reports_root / "state_hash.txt"
    if state_hash_path.exists():
        state_hash = state_hash_path.read_text(encoding="utf-8").strip()

    event_batch_hash = None
    event_batch_path = reports_root / "event_ledger_receipt.json"
    if event_batch_path.exists():
        event_batch_hash = _load_json(event_batch_path).get("batch_hash")

    material = json.dumps({
        "previous_provenance_hash": prev_hash,
        "state_hash": state_hash,
        "event_batch_hash": event_batch_hash,
    }, sort_keys=True)

    prov_hash = _sha256_text(material)
    step = {
        "provenance_version": "1.0",
        "step_id": f"provenance_step_{next_idx:04d}",
        "previous_step_id": prev_id,
        "previous_provenance_hash": prev_hash,
        "state_hash": state_hash,
        "event_batch_hash": event_batch_hash,
        "provenance_hash": prov_hash,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

    (prov_dir / f"{step['step_id']}.json").write_text(json.dumps(step, indent=2), encoding="utf-8")
    (prov_dir / "latest_provenance_step.json").write_text(
        json.dumps({"latest_step": step["step_id"], "latest_hash": prov_hash}, indent=2),
        encoding="utf-8"
    )

    lines = []
    for p in sorted(prov_dir.glob("provenance_step_*.json")):
        d = _load_json(p)
        lines.append(f"{d['step_id']} | prev={d.get('previous_step_id')} | hash={d['provenance_hash']}")
    (prov_dir / "provenance_chain.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return step

def verify_provenance_chain(root: Path) -> dict:
    reports_root = root / "reports"
    prov_dir = reports_root / "provenance_chain"
    if not prov_dir.exists():
        return {"status": "FAIL", "step_count": 0, "failures": ["provenance_chain_missing"]}

    steps = sorted(prov_dir.glob("provenance_step_*.json"))
    failures = []
    prev_hash = None
    prev_id = None

    for s in steps:
        step = _load_json(s)
        material = json.dumps({
            "previous_provenance_hash": step.get("previous_provenance_hash"),
            "state_hash": step.get("state_hash"),
            "event_batch_hash": step.get("event_batch_hash"),
        }, sort_keys=True)
        recomputed = _sha256_text(material)
        if recomputed != step.get("provenance_hash"):
            failures.append(f"{step['step_id']}:hash_mismatch")
        if prev_id is None:
            if step.get("previous_step_id") is not None:
                failures.append(f"{step['step_id']}:root_invalid")
        else:
            if step.get("previous_step_id") != prev_id:
                failures.append(f"{step['step_id']}:prev_id_mismatch")
            if step.get("previous_provenance_hash") != prev_hash:
                failures.append(f"{step['step_id']}:prev_hash_mismatch")
        prev_id = step.get("step_id")
        prev_hash = step.get("provenance_hash")

    return {
        "status": "PASS" if not failures else "FAIL",
        "step_count": len(steps),
        "failures": failures,
    }

def write_provenance_reports(root: Path, step: dict, verification: dict):
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "provenance_receipt.json").write_text(json.dumps(step, indent=2), encoding="utf-8")
    (reports_root / "provenance_verification.json").write_text(json.dumps(verification, indent=2), encoding="utf-8")
    lines = [
        "# Unified Provenance Verification",
        "",
        f"- Status: **{verification['status']}**",
        f"- Step count: `{verification.get('step_count', 0)}`",
        f"- Latest step: `{step.get('step_id')}`",
        f"- Provenance hash: `{step.get('provenance_hash')}`",
    ]
    (reports_root / "provenance_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")