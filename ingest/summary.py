from __future__ import annotations
from pathlib import Path

def write_summary(reports_root: Path, receipt: dict, state_record: dict, report: dict):
    reports_root.mkdir(parents=True, exist_ok=True)

    summary = f"""
StegVerse Deterministic Execution Report
========================================

Run Mode: {report.get("mode")}
Source: {report.get("source")}
Timestamp: {receipt.get("timestamp_utc")}

Bundle Hash:
{receipt.get("bundle_hash")}

State Transition:
Previous: {state_record.get("previous_state_id")}
Current:  {state_record.get("state_id")}

State Hash:
{state_record.get("state_hash")}

Execution Receipt File:
execution_receipt.json

Artifact Hash File:
artifact_hash.txt

State Graph Location:
reports/state_graph/
"""

    (reports_root / "summary.md").write_text(summary.strip() + "\n", encoding="utf-8")