from __future__ import annotations
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def load_repos_config():
    return json.loads((ROOT / "configs" / "repos.json").read_text(encoding="utf-8"))
