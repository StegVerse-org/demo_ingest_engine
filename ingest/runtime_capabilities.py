from __future__ import annotations

from pathlib import Path
from datetime import datetime
import importlib.util
import json


def detect_capabilities() -> dict:
    matplotlib_available = importlib.util.find_spec("matplotlib") is not None

    return {
        "capabilities_version": "1.0",
        "matplotlib_available": matplotlib_available,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }


def write_capability_reports(reports_root: Path, capabilities: dict) -> None:
    reports_root.mkdir(parents=True, exist_ok=True)

    (reports_root / "runtime_capabilities.json").write_text(
        json.dumps(capabilities, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Runtime Capabilities",
        "",
        f"- Matplotlib available: `{capabilities['matplotlib_available']}`",
        f"- Timestamp: `{capabilities['timestamp_utc']}`",
        "",
    ]

    (reports_root / "runtime_capabilities.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def write_stage_status(
    reports_root: Path,
    stage_name: str,
    status: str,
    message: str,
    extra: dict | None = None,
) -> None:
    reports_root.mkdir(parents=True, exist_ok=True)

    payload = {
        "stage": stage_name,
        "status": status,
        "message": message,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }
    if extra:
        payload["extra"] = extra

    (reports_root / f"{stage_name}_stage_status.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )