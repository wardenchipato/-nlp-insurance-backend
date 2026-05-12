import os

# backend/ (contains app/, knowledge/, data/, …)
_BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Repository root (parent of backend/) — some setups drop .txt files here by mistake
_REPO_ROOT = os.path.abspath(os.path.join(_BACKEND_ROOT, ".."))

KNOWLEDGE_DIR = os.path.join(_BACKEND_ROOT, "knowledge")
LOCAL_DB_PATH = os.path.join(_BACKEND_ROOT, "data", "kb.sqlite")


def knowledge_scan_roots() -> list[str]:
    """
    Directories scanned for *.txt corpus files (uploads still go to KNOWLEDGE_DIR).
    Order matters: first directory wins when the same basename exists in two places.
    """
    roots = [
        KNOWLEDGE_DIR,
        os.path.join(_REPO_ROOT, "knowledge"),
    ]
    seen: set[str] = set()
    out: list[str] = []
    for r in roots:
        ar = os.path.abspath(r)
        if ar not in seen:
            seen.add(ar)
            out.append(ar)
    return out


def ensure_kb_dirs() -> None:
    os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(LOCAL_DB_PATH), exist_ok=True)
