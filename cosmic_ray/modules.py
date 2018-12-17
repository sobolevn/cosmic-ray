"""Functions related to finding modules for testing."""

import glob
from pathlib import Path


def find_modules(module_path):
    """Find all modules in the module (possibly package) represented by `module_path`.

    Args:
        module_path: A pathlib.Path to a Python package or module.

    Returns: An iterable of paths Python modules (i.e. *py files).
    """
    if module_path.is_file():
        if module_path.suffix == '.py':
            yield module_path
    elif module_path.is_dir():
        pyfiles = glob.glob('{}/**/*.py'.format(module_path), recursive=True)
        yield from (Path(pyfile) for pyfile in pyfiles)
