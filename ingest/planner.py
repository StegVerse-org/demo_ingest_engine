from __future__ import annotations
from pathlib import Path
from .detect import relative_files
from .validate import is_allowed

def build_plan(source_dir: Path, target_repo: Path, allowed_prefixes: list[str], repo_name: str):
    rels, real_source = relative_files(source_dir)
    added, replaced, skipped = [], [], []
    for rel in rels:
        rel_str = rel.as_posix()
        if not is_allowed(rel_str, allowed_prefixes):
            skipped.append(rel_str); continue
        dest = target_repo / rel
        if dest.exists():
            replaced.append(rel_str)
        else:
            added.append(rel_str)
    return {"repo": repo_name, "source_root": str(real_source), "target_root": str(target_repo), "added": sorted(added), "replaced": sorted(replaced), "skipped": sorted(skipped)}
