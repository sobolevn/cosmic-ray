import contextlib
import os
from pathlib import Path
import sys


_THIS_DIR = Path(
    os.path.dirname(
        os.path.realpath(__file__)))

# TODO: this should be a fixture.
DATA_DIR = _THIS_DIR / 'data'


@contextlib.contextmanager
def excursion(directory):
    """Context manager for temporarily setting `directory` as the current working
    directory.
    """
    old_dir = os.getcwd()
    os.chdir(str(directory))
    try:
        yield
    finally:
        os.chdir(old_dir)
