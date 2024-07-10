# Module Reloader

`module_reloader` is a Python package that provides functionality to track and reload 
modules dynamically. It helps you manage module reloading in a controlled manner, 
making it useful for development environments where you need to reload modules frequently.

## Why `module_reloader`?

This package was created to facilitate REPL-driven development in Python, similar to the 
workflow experienced in languages like Clojure. In such a workflow, developers often modify 
their code and want to see the changes reflected immediately without restarting their 
entire application. `module_reloader` aims to provide an efficient and easy way to reload 
modules dynamically, enabling a more interactive and productive development experience.

## Features

- Track loaded modules and their load times.
- Reload specific modules by name or by file path.
- Identify and reload stale modules (modules that have been modified since they were last loaded).

## Installation

You can install the package directly from the source directory:

```sh
pip install .
```

Or install it in editable mode (useful for development):

```sh
pip install -e .
```

## Usage

### Application startup
When your program starts up, import module_reloader before importing any other application-level 
modules. module_reloader will then keep track of these loaded modules automatically.

```Python
import module_reloader
```

### Reloading a single module
When you're working within a single module and wants to reload it, you can simply send the
full path of the module you're trying to reload:

```Python
module_reloader.reload_module_by_path("full/path/to/module/here")
```

It should be fairly straightforward to configure your favorite editor to send that string
along with the path of the module/file you're working with directly to the REPL.

### Reloading multiple modules
If you're working with multiple modules all at once, you can also simply choose to do:

```Python
module_reloader.reload_stale_modules()
```

`module_reloader` will then look through all modules it has been tracking and reload any
module that has been changed since it was last loaded.

## Caveat

### Avoid `from ... import ...`
Creating references to functions and variables using `from ... import ...` can be 
problematic because these references will not be updated when the module is reloaded. 

Instead, it is recommended to use `import ... as ...` to alias the module name and 
access its contents through the module object. This ensures that you always access 
the updated functions and variables.

### Class instances
Module reloading will have no effect on classes that have already been instantiated. 
If you need to update instances of a class after reloading the module, you will 
need to recreate those instances.

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License.
