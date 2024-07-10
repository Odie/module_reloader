import importlib
import importlib.abc
import importlib.util
import importlib.machinery
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LoadedModuleInfo:
    module_name: str
    path: str
    load_time: float = field(default_factory=lambda: time.time())


# Dictionary to keep track of loaded modules and their load times
loaded_modules: Dict[str, LoadedModuleInfo] = {}


def track_module(spec: importlib.machinery.ModuleSpec) -> None:
    # If we haven't been tracking this module before...
    if spec.name not in loaded_modules:
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


def get_stale_modules() -> List[str]:
    stale_modules = []
    for module_name, info in loaded_modules.items():
        module_file = sys.modules[module_name].__file__
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

# Example usage
if __name__ == "__main__":
    print("---------- Creating ModuleA.hello_world() ----------")
    with open("ModuleA.py", "w") as f:
        f.write("def hello_world():\n")
        f.write('    print("Hello, world!")\n')

    import ModuleA  # This will be tracked automatically
    from ModuleA import hello_world

    print("Loaded modules:", get_loaded_modules())
    print("")

    print("---------- Calling ModuleA.hello_world() ----------")
    ModuleA.hello_world()
    print("\n")

    # Simulate modifying ModuleA.py and then reloading stale modules
    print("---------- Modifying ModuleA.hello_world() ----------")
    with open("ModuleA.py", "w") as f:
        f.write("def hello_world():\n")
        f.write('    print("Hello, new world!")\n')

    print("---------- Checking stale modules ----------")
    stale = get_stale_modules()
    print("Stale modules:", stale)
    print("")

    print("---------- Reloading ModuleA ----------")
    reload_module("ModuleA")
    print("")

    print("---------- Calling ModuleA.hello_world() ----------")
    ModuleA.hello_world()
    print("")
