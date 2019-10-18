# External
from importlib_metadata import version

# Project
from .cpu_count import cpu_count
from .monkey_patch import setup_monkey_patch

try:
    __version__ = version(__name__)  # type: str
except Exception:  # pragma: no cover
    import traceback
    from warnings import warn

    warn("Failed to set version due to:\n" + traceback.format_exc(), ImportWarning)
    __version__ = "0.0a0"

__all__ = ("__version__", "cpu_count", "setup_monkey_patch")
