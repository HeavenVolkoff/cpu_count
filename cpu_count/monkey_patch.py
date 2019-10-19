# Internal
import sys
import typing as T
from types import ModuleType
from functools import update_wrapper
from importlib import reload, import_module, invalidate_caches
from importlib.machinery import ModuleSpec, BuiltinImporter

# Project
from .cpu_count import cpu_count


class MoneyPatchBuiltinImporter(BuiltinImporter):
    @classmethod
    def exec_module(cls, module: ModuleType) -> None:
        super().exec_module(module)

        # Patches are done here
        setattr(module, "cpu_count", update_wrapper(cpu_count, getattr(module, "cpu_count")))

    @classmethod
    def find_spec(
        cls,
        fullname: str,
        path: T.Optional[T.Sequence[T.Union[bytes, str]]] = None,
        target: T.Optional[ModuleType] = None,
    ) -> T.Optional[ModuleSpec]:
        """Only execute on known monkey_patched modules.
        Doing so allows non patched modules to fallthrough and be handled by other module loaders
        """
        return super().find_spec(fullname, path, target) if fullname == "posix" else None


def setup_monkey_patch() -> None:
    # Only register our custom loader once
    if not any(isinstance(importer, MoneyPatchBuiltinImporter) for importer in sys.meta_path):
        # Insert it at the begin of the modules loaders list,
        # in order for it to take precedence over the standard loaders
        sys.meta_path.insert(0, MoneyPatchBuiltinImporter())
        # Invalidate all module caches to force new versions to load
        invalidate_caches()
        # Reload `posix` so it goes through our loader
        reload(import_module("posix"))
        # Most of `os` functions are re-exports from `posix`
        # So in order for it to use our new monkey-patched versions we need to
        # reload it too.
        reload(import_module("os"))
