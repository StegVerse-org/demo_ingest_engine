from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json
import zipfile


PRIORITY_REPORTS = [
    "summary.md",
    "policy_surface.md",
    "policy_surface_matrix.md",
    "phase_diagram.md",
    "phase_diagram_mermaid.md",
    "paper_metrics_summary.md",
    "full_system_verification.md",
    "runtime_manifest.json",
    "report_index.md",
    "visualization_manifest.md",
    "stress_test_results.json",
    "phase_diagram.json",
    "paper_metrics.json",
    "full_system_verification.json",
]


def build_publication_summary(reports_root: Path) -> dict:
    present = []
    missing = []

    for rel in PRIORITY_REPORTS:
        p = reports_root / rel
        if p.exists():
            present.append(rel)
        else:
            missing.append(rel)

    summary = {
        "publication_summary_version": "1.0",
        "present_reports": present,
        "missing_reports": missing,
        "present_count": len(present),
        "missing_count": len(missing),
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }
    return summary


def write_publication_summary(reports_root: Path, summary: dict) -> None:
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "publication_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    lines = [
        "# Publication Summary",
        "",
        f"- Present reports: `{summary['present_count']}`",
        f"- Missing reports: `{summary['missing_count']}`",
        "",
        "## Present",
        "",
    ]
    if summary["present_reports"]:
        for item in summary["present_reports"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")

    lines += ["", "## Missing", ""]
    if summary["missing_reports"]:
        for item in summary["missing_reports"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")

    (reports_root / "publication_summary.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def build_demo_packet(reports_root: Path) -> dict:
    packet_dir = reports_root / "demo_packet"
    packet_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    for rel in PRIORITY_REPORTS:
        src = reports_root / rel
        if src.exists():
            dst = packet_dir / src.name
            dst.write_bytes(src.read_bytes())
            copied.append(src.name)

    payload = {
        "demo_packet_version": "1.0",
        "file_count": len(copied),
        "files": copied,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }
    (packet_dir / "demo_packet_manifest.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    zip_path = reports_root / "demo_packet.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(packet_dir.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(reports_root))

    return {
        "demo_packet_version": "1.0",
        "packet_dir": str(packet_dir.relative_to(reports_root)),
        "zip_name": zip_path.name,
        "file_count": len(copied),
        "files": copied,
    }


def write_demo_packet_report(reports_root: Path, packet: dict) -> None:
    (reports_root / "demo_packet_report.json").write_text(
        json.dumps(packet, indent=2), encoding="utf-8"
    )

    lines = [
        "# Demo Packet Report",
        "",
        f"- Packet dir: `{packet['packet_dir']}`",
        f"- Zip name: `{packet['zip_name']}`",
        f"- File count: `{packet['file_count']}`",
        "",
        "## Files",
        "",
    ]
    if packet["files"]:
        for name in packet["files"]:
            lines.append(f"- `{name}`")
    else:
        lines.append("- none")

    (reports_root / "demo_packet_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )