import shutil
from .detect import relative_files
from .validate import is_allowed

def install_files(source_dir, target_repo, allowed_prefixes, archive, archive_root, repo_name):
    rels, real_source = relative_files(source_dir)
    added, replaced, skipped, archived = [], [], [], []
    for rel in rels:
        s = rel.as_posix()
        if s == 'BUNDLE_MANIFEST.json': continue
        if not is_allowed(s, allowed_prefixes): skipped.append(s); continue
        src = real_source / rel; dest = target_repo / rel; dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            if archive:
                a = archive_root / repo_name / rel; a.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(dest), str(a)); archived.append(s)
            else:
                if dest.is_file(): dest.unlink()
            replaced.append(s)
        else: added.append(s)
        shutil.copy2(src, dest)
    return {'repo': repo_name, 'added': sorted(added), 'replaced': sorted(replaced), 'skipped': sorted(skipped), 'archived': sorted(archived)}
