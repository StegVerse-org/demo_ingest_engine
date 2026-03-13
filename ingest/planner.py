from .detect import relative_files
from .validate import is_allowed

def build_plan(source_dir, target_repo, allowed_prefixes, repo_name):
    rels, real_source = relative_files(source_dir)
    added, replaced, skipped = [], [], []
    for rel in rels:
        s = rel.as_posix()
        if s == 'BUNDLE_MANIFEST.json': continue
        if not is_allowed(s, allowed_prefixes): skipped.append(s); continue
        (replaced if (target_repo/rel).exists() else added).append(s)
    return {'repo': repo_name, 'source_root': str(real_source), 'target_root': str(target_repo), 'added': sorted(added), 'replaced': sorted(replaced), 'skipped': sorted(skipped)}
