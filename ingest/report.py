from pathlib import Path
import json

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data, indent=2), encoding='utf-8')

def build_markdown(report: dict) -> str:
    lines = ['# Ingestion report','',f"- Mode: `{report['mode']}`",f"- Source: `{report['source']}`",f"- Conflict mode: `{report['conflict_mode']}`",f"- Apply mode: `{report['apply_mode']}`"]
    if report.get('bundle_manifest'):
        lines += [f"- Bundle name: `{report['bundle_manifest'].get('bundle_name')}`", f"- Bundle version: `{report['bundle_manifest'].get('bundle_version')}`"]
    lines.append('')
    for t in report['targets']:
        lines += [f"## {t['repo']}",'',f"- Added: `{len(t['added'])}`",f"- Replaced: `{len(t['replaced'])}`",f"- Skipped: `{len(t['skipped'])}`",f"- Archived: `{len(t.get('archived', []))}`",'']
    return '\n'.join(lines)+'\n'

def write_markdown(path: Path, report: dict):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(build_markdown(report), encoding='utf-8')
