from __future__ import annotations
from pathlib import Path
import json

def load_run_profiles(path: Path) -> dict:
    if not path.exists():
        return {
            "profiles": {
                "demo": {
                    "experiment": False,
                    "stress_test": False,
                    "policy_surface": False,
                    "phase_diagram": False,
                    "adversarial": False,
                    "paper_reports": False,
                    "coordinated_batch": False,
                    "unified_verify": False,
                    "actuation_plan": False,
                    "visuals": False,
                    "full_verify": False,
                },
                "research": {
                    "experiment": True,
                    "stress_test": True,
                    "policy_surface": True,
                    "phase_diagram": True,
                    "adversarial": True,
                    "paper_reports": True,
                    "coordinated_batch": True,
                    "unified_verify": True,
                    "actuation_plan": True,
                    "visuals": True,
                    "full_verify": True,
                }
            }
        }
    return json.loads(path.read_text(encoding="utf-8"))

def apply_profile(args, profile_name: str, profiles: dict):
    profile = profiles.get("profiles", {}).get(profile_name, {})
    for key, value in profile.items():
        if hasattr(args, key):
            setattr(args, key, value)
    return profile

def write_run_profile_report(reports_root: Path, profile_name: str, applied: dict):
    reports_root.mkdir(parents=True, exist_ok=True)
    payload = {
        "profile_name": profile_name,
        "applied_flags": applied,
    }
    (reports_root / "run_profile.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")