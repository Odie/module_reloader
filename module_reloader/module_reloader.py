import importlib
import importlib.abc
import importlib.util
import importlib.machinery
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LoadedModuleInfo:
    module_name: str
    path: str
    load_time: float = field(default_factory=lambda: time.time())


# Dictionary to keep track of loaded modules and their load times
loaded_modules: Dict[str, LoadedModuleInfo] = {}


def track_module(spec: importlib.machinery.ModuleSpec) -> None:
    # If we haven't been tracking this module before...
    if spec.name not in loaded_modules and spec.origin:
        assert spec.origin

        # Setup an entry to track this module...
        loaded_modules[spec.name] = LoadedModuleInfo(
            module_name=spec.name, path=spec.origin, load_time=time.time()
        )


def update_module_load_time(module_name: str) -> None:
    # If we've already started tracking the module, update the load time
    if module_name in loaded_modules:
        loaded_modules[module_name].load_time = time.time()


def get_loaded_modules() -> Dict[str, LoadedModuleInfo]:
    return loaded_modules


def reload_module(module_name: str) -> None:
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
        update_module_load_time(module_name)


def reload_module_by_path(module_path: str) -> None:
    for module_name, info in loaded_modules.items():
        if info.path == module_path:
            reload_module(module_name)
            return
    logger.error(f"No module found with path '{module_path}'")


def get_stale_modules() -> List[str]:
    stale_modules = []
    for module_name, info in loaded_modules.items():
        try:
            module_file = sys.modules[module_name].__file__
        except (KeyError, AttributeError):
            continue

        if module_file:
            mod_time = os.path.getmtime(module_file)
            if mod_time > info.load_time:
                stale_modules.append(module_name)
    return stale_modules


def reload_stale_modules() -> None:
    for module_name in get_stale_modules():
        reload_module(module_name)


class CustomImportFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        for finder in sys.meta_path[1:]:
            if hasattr(finder, "find_spec"):
                spec = finder.find_spec(fullname, path, target)
                if spec is not None:
                    track_module(spec)
                    return spec
        return None


# Insert the custom import finder into the meta path
sys.meta_path.insert(0, CustomImportFinder())
