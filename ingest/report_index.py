from __future__ import annotations
from pathlib import Path
import json

def build_report_index(reports_root: Path) -> dict:
    items = []
    for p in sorted(reports_root.rglob("*")):
        if p.is_file():
            items.append({
                "path": str(p.relative_to(reports_root)),
                "suffix": p.suffix.lower(),
                "size_bytes": p.stat().st_size,
            })
    return {
        "report_index_version": "1.0",
        "report_count": len(items),
        "reports": items,
    }

def write_report_index(reports_root: Path, index_data: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "report_index.json").write_text(json.dumps(index_data, indent=2), encoding="utf-8")

    lines = [
        "# Report Index",
        "",
        f"- Report count: `{index_data['report_count']}`",
        "",
        "| Path | Type | Size |",
        "|---|---|---:|",
    ]
    for item in index_data["reports"]:
        lines.append(f"| {item['path']} | {item['suffix'] or 'none'} | {item['size_bytes']} |")
    (reports_root / "report_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")