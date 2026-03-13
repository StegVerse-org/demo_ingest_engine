from __future__ import annotations
from pathlib import Path

def list_entities(root: Path) -> list[str]:
    entities_dir = root / "entities"
    if not entities_dir.exists():
        return []
    return sorted([p.name for p in entities_dir.iterdir() if p.is_dir()])

def resolve_entities(root: Path, entity: str | None = None, all_entities: bool = False) -> list[str]:
    available = list_entities(root)
    if all_entities:
        return available
    if entity:
        if entity not in available:
            raise ValueError(f"Unknown entity: {entity}")
        return [entity]
    return ["default"]

def reports_root_for_entity(root: Path, entity_name: str) -> Path:
    if entity_name == "default":
        return root / "reports"
    return root / "entities" / entity_name / "reports"