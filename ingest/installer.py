from __future__ import annotations
from pathlib import Path
import shutil
from .detect import relative_files
from .validate import is_allowed

def install_files(source_dir: Path, target_repo: Path, allowed_prefixes: list[str], archive: bool, archive_root: Path, repo_name: str):
    rels, real_source = relative_files(source_dir)
    added, replaced, skipped, archived = [], [], [], []
    for rel in rels:
        rel_str = rel.as_posix()
        if not is_allowed(rel_str, allowed_prefixes):
            skipped.append(rel_str); continue
        src = real_source / rel
        dest = target_repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            if archive:
                archive_dest = archive_root / repo_name / rel
                archive_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dest), str(archive_dest))
                archived.append(rel_str)
            else:
                if dest.is_file():
                    dest.unlink()
            replaced.append(rel_str)
        else:
            added.append(rel_str)
        shutil.copy2(src, dest)
    return {"repo": repo_name, "added": sorted(added), "replaced": sorted(replaced), "skipped": sorted(skipped), "archived": sorted(archived)}
