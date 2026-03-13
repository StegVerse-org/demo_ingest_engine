from pathlib import Path
import shutil, subprocess

def clone_repo(repo_url: str, target_dir: Path, branch: str='main'):
    if target_dir.exists(): shutil.rmtree(target_dir)
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git','clone','--branch',branch,repo_url,str(target_dir)], check=True)
