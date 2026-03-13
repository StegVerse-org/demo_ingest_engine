from __future__ import annotations
from pathlib import Path
import json

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def run_full_system_verification(reports_root: Path) -> dict:
    checks_passed = []
    checks_failed = []

    expected_json = {
        "verification_report.json": "status",
        "replay_verification.json": "status",
        "event_replay_verification.json": "status",
        "event_ledger_verification.json": "status",
        "provenance_verification.json": "status",
        "unified_provenance_verification.json": "status",
    }

    for filename, field in expected_json.items():
        path = reports_root / filename
        if not path.exists():
            checks_failed.append(f"missing:{filename}")
            continue
        data = _load_json(path)
        value = data.get(field)
        if value == "PASS":
            checks_passed.append(f"pass:{filename}")
        else:
            checks_failed.append(f"not_pass:{filename}")

    expected_files = [
        "summary.md",
        "policy_surface.md",
        "phase_diagram.md",
        "paper_metrics_summary.md",
    ]
    for filename in expected_files:
        path = reports_root / filename
        if path.exists():
            checks_passed.append(f"present:{filename}")
        else:
            checks_failed.append(f"missing:{filename}")

    return {
        "full_system_verification_version": "1.0",
        "status": "PASS" if not checks_failed else "FAIL",
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
    }

def write_full_system_verification(reports_root: Path, result: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    (reports_root / "full_system_verification.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )

    lines = [
        "# Full System Verification",
        "",
        f"- Status: **{result['status']}**",
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
    (reports_root / "full_system_verification.md").write_text("\n".join(lines) + "\n", encoding="utf-8")