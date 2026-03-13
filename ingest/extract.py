from pathlib import Path
import zipfile, shutil

def extract_if_zip(source: Path, staging_root: Path) -> Path:
    if source.is_file() and source.suffix.lower()=='.zip':
        dest = staging_root / source.stem
        if dest.exists(): shutil.rmtree(dest)
        dest.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(source,'r') as z: z.extractall(dest)
        return dest
    return source
