from pathlib import Path
import sys


def setup_backend_path() -> Path:
    backend_path = Path(__file__).resolve().parents[2] / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    return backend_path
