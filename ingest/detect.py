from pathlib import Path

def flatten_if_single_root(source_dir: Path) -> Path:
    entries = [p for p in source_dir.iterdir()]
    return entries[0] if len(entries)==1 and entries[0].is_dir() else source_dir

def relative_files(source_dir: Path):
    source_dir = flatten_if_single_root(source_dir)
    return [p.relative_to(source_dir) for p in source_dir.rglob('*') if p.is_file()], source_dir

def discover_zip_bundles(incoming_dir: Path):
    return sorted([p for p in incoming_dir.iterdir() if p.is_file() and p.suffix.lower()=='.zip'])
