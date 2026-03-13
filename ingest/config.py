from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
def load_repos_config(): return json.loads((ROOT/'configs'/'repos.json').read_text(encoding='utf-8'))
def load_manifest_schema(): return json.loads((ROOT/'configs'/'manifest_schema.json').read_text(encoding='utf-8'))
