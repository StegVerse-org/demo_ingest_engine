from __future__ import annotations

def is_allowed(rel_path: str, allowed_prefixes: list[str]) -> bool:
    for prefix in allowed_prefixes:
        if prefix.endswith("/"):
            if rel_path.startswith(prefix):
                return True
        else:
            if rel_path == prefix:
                return True
    return False
