from pathlib import Path

_PROJECT_ROOT = None


def init_project_root(root):
    """Set the project root used for config and data paths."""
    global _PROJECT_ROOT
    _PROJECT_ROOT = Path(root).resolve()


def get_project_root():
    """Return the repository root directory."""
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT

    return Path(__file__).resolve().parent.parent


def get_config_path(filename):
    """Resolve a config file path from common project locations."""
    candidates = [
        get_project_root() / 'config' / filename,
        Path.cwd() / 'config' / filename,
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]
