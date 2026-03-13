from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

def classify_mutation(source: Path, mode: str) -> dict:
    source_name = source.name.lower()
    mutation_type = "unknown_mutation"
    confidence = 0.5

    if source.is_dir():
        mutation_type = "artifact_ingestion"
        confidence = 1.0
    elif source_name.endswith(".json") and "policy" in source_name:
        mutation_type = "policy_change"
        confidence = 0.95
    elif source_name.endswith(".json") and "config" in source_name:
        mutation_type = "configuration_change"
        confidence = 0.95
    elif source_name.endswith(".zip"):
        mutation_type = "artifact_ingestion"
        confidence = 0.95
    elif source_name.endswith(".md"):
        mutation_type = "documentation_change"
        confidence = 0.85

    return {
        "receipt_version": "1.0",
        "mutation_type": mutation_type,
        "mode": mode,
        "source": str(source),
        "classification_confidence": confidence,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

def write_mutation_receipt(reports_root: Path, receipt: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "mutation_receipt.json").write_text(
        json.dumps(receipt, indent=2), encoding="utf-8"
    )