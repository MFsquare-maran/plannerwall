# utils/env.py
def pick(d: dict, path: str):
    """Sicherer Zugriff auf verschachtelte Dict-Felder via 'aare.temperature'."""
    cur = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur
