from pathlib import Path
import datetime, shutil

ARCHIVE_ROOT = Path("deprecated")

def archive_file(path: Path):

    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    dest = ARCHIVE_ROOT / ts / path

    dest.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(str(path), str(dest))
