def is_allowed(rel_path: str, allowed_prefixes: list[str]) -> bool:
    for prefix in allowed_prefixes:
        if prefix.endswith('/') and rel_path.startswith(prefix): return True
        if rel_path == prefix: return True
    return False
