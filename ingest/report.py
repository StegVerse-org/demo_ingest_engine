from __future__ import annotations
from pathlib import Path
import json

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def build_markdown(report: dict) -> str:
    lines = ["# Ingestion report", "", f"- Mode: `{report['mode']}`", f"- Source: `{report['source']}`", f"- Conflict mode: `{report['conflict_mode']}`", f"- Apply mode: `{report['apply_mode']}`"]
    if report.get("bundle_manifest"):
        lines.extend([f"- Bundle name: `{report['bundle_manifest'].get('bundle_name')}`", f"- Bundle version: `{report['bundle_manifest'].get('bundle_version')}`"])
    lines.append("")
    for target in report["targets"]:
        lines.extend([f"## {target['repo']}", "", f"- Added: `{len(target['added'])}`", f"- Replaced: `{len(target['replaced'])}`", f"- Skipped: `{len(target['skipped'])}`", f"- Archived: `{len(target.get('archived', []))}`", ""])
    return "\n".join(lines) + "\n"

def write_markdown(path: Path, report: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_markdown(report), encoding="utf-8")
