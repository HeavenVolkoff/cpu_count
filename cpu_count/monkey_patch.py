# Internal
import sys
from types import ModuleType
from functools import update_wrapper
from importlib import reload, import_module, invalidate_caches
from importlib.machinery import BuiltinImporter

# Project
from .cpu_count import cpu_count


class MoneyPatchBuiltinImporter(BuiltinImporter):
    @classmethod
    def exec_module(cls, module: ModuleType) -> None:
        super().exec_module(module)

        if module.__name__ == "posix":
            setattr(module, "cpu_count", update_wrapper(cpu_count, getattr(module, "cpu_count")))


def setup_monkey_patch() -> None:
    # Only register our custom loader once
    if MoneyPatchBuiltinImporter not in sys.meta_path:
        # Insert it first in the list of modules loaders
        sys.meta_path.insert(0, MoneyPatchBuiltinImporter())
        # Invalidate all module caches to force new versions to be loaded
        invalidate_caches()
        # Reload `posix` to force it to use our CustomFinder
        reload(import_module("posix"))
        # Most of `os` functions are re-exports from `posix`.
        # So in order for it to use the new monkey-patched version of cpu_count
        # we need to reload it.
        reload(import_module("os"))
