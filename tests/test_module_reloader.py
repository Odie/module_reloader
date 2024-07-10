import unittest
import os
import time
import importlib
import sys
from module_reloader import (
    track_module,
    update_module_load_time,
    get_loaded_modules,
    reload_module,
    reload_module_by_path,
    get_stale_modules,
    reload_stale_modules,
    loaded_modules,
)


def spit(filename, content):
    with open(filename, "w") as f:
        f.write(content)


class TestModuleReloader(unittest.TestCase):
    def setUp(self):
        # Set up a temporary module for testing
        self.module_name = "ModuleA"
        self.module_code_initial = "def hello_world():\n    print('Hello, world!')\n"
        self.module_code_modified = (
            "def hello_world():\n    print('Hello, new world!')\n"
        )
        self.module_filename = f"{self.module_name}.py"

        spit(self.module_filename, self.module_code_initial)

        # Ensure the module is loaded and tracked
        importlib.invalidate_caches()
        import ModuleA

        track_module(importlib.util.find_spec(self.module_name))

    def tearDown(self):
        # Clean up by removing the temporary module file
        os.remove(self.module_filename)
        loaded_modules.clear()
        if self.module_name in sys.modules:
            del sys.modules[self.module_name]

    def test_track_module(self):
        self.assertIn(self.module_name, loaded_modules)
        info = loaded_modules[self.module_name]
        self.assertEqual(info.module_name, self.module_name)
        self.assertTrue(os.path.isfile(info.path))

    def test_update_module_load_time(self):
        original_load_time = loaded_modules[self.module_name].load_time
        update_module_load_time(self.module_name)
        self.assertGreater(
            loaded_modules[self.module_name].load_time, original_load_time
        )

    def test_get_loaded_modules(self):
        modules = get_loaded_modules()
        self.assertIn(self.module_name, modules)

    def test_reload_module(self):
        original_load_time = loaded_modules[self.module_name].load_time
        spit(self.module_filename, self.module_code_modified)

        reload_module(self.module_name)
        self.assertGreater(
            loaded_modules[self.module_name].load_time, original_load_time
        )

    def test_reload_module_by_path(self):
        spit(self.module_filename, self.module_code_modified)

        reload_module_by_path(os.path.abspath(self.module_filename))
        self.assertIn(self.module_name, sys.modules)

    def test_get_stale_modules(self):
        spit(self.module_filename, self.module_code_modified)

        stale_modules = get_stale_modules()
        self.assertIn(self.module_name, stale_modules)

    def test_reload_stale_modules(self):
        spit(self.module_filename, self.module_code_modified)

        stale_modules = get_stale_modules()
        self.assertIn(self.module_name, stale_modules)

        reload_stale_modules()
        self.assertNotIn(self.module_name, get_stale_modules())


if __name__ == "__main__":
    unittest.main()
