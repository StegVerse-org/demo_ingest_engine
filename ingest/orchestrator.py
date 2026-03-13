from __future__ import annotations
from pathlib import Path
from .config import load_repos_config
from .git_ops import clone_repo
from .planner import build_plan
from .installer import install_files

def resolve_targets(target_repo: str | None, target_set: str | None):
    cfg = load_repos_config()
    if target_set:
        return cfg["target_sets"][target_set]
    if target_repo:
        return [target_repo]
    raise ValueError("Either target_repo or target_set must be provided")

def prepare_targets(target_names: list[str], work_root: Path):
    cfg = load_repos_config()
    prepared = {}
    for name in target_names:
        repo_cfg = cfg["repos"][name]
        repo_dir = work_root / name
        clone_repo(repo_cfg["clone_url"], repo_dir, branch=repo_cfg["default_branch"])
        prepared[name] = {"dir": repo_dir, "config": repo_cfg}
    return prepared

def orchestrate_plan(source_dir: Path, target_names: list[str], work_root: Path):
    prepared = prepare_targets(target_names, work_root)
    return [build_plan(source_dir, item["dir"], item["config"]["allowed_prefixes"], name) for name, item in prepared.items()]

def orchestrate_install(source_dir: Path, target_names: list[str], work_root: Path, archive_root: Path, archive: bool):
    prepared = prepare_targets(target_names, work_root)
    targets = [install_files(source_dir, item["dir"], item["config"]["allowed_prefixes"], archive, archive_root, name) for name, item in prepared.items()]
    return targets
