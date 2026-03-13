import zipfile
from pathlib import Path
import shutil

STAGING = Path("staging")

def extract_if_zip(source: Path) -> Path:

    if source.is_file() and source.suffix == ".zip":

        dest = STAGING / source.stem

        if dest.exists():
            shutil.rmtree(dest)

        dest.mkdir(parents=True)

        with zipfile.ZipFile(source,"r") as z:
            z.extractall(dest)

        return dest

    return source
