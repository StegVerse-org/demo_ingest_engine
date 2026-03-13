from pathlib import Path
import shutil
from .archive import archive_file

def install_bundle(source_dir: Path, target_repo: Path, archive=False):

    for src in source_dir.rglob("*"):

        if src.is_dir():
            continue

        rel = src.relative_to(source_dir)

        dest = target_repo / rel

        dest.parent.mkdir(parents=True, exist_ok=True)

        if dest.exists():

            if archive:
                archive_file(dest)
            else:
                dest.unlink()

        shutil.copy2(src, dest)

    print("Install complete")
