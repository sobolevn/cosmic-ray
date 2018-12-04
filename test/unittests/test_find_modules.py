from pathlib import Path

from cosmic_ray.modules import find_modules
from path_utils import DATA_DIR


def test_small_directory_tree():
    datadir = DATA_DIR
    paths = (('a', '__init__.py'),
             ('a', 'b.py'),
             ('a', 'py.py'),
             ('a', 'c', '__init__.py'),
             ('a', 'c', 'd.py'))
    expected = sorted(datadir / Path(*path) for path in paths)
    results = sorted(find_modules(datadir / 'a'))
    assert expected == results


def test_finding_modules_via_dir_name():
    datadir = DATA_DIR
    paths = (('a', 'c', '__init__.py'),
             ('a', 'c', 'd.py'))
    expected = sorted(datadir / Path(*path) for path in paths)
    results = sorted(find_modules(datadir / 'a' / 'c'))
    assert expected == results


def test_finding_modules_via_dir_name_and_filename_ending_in_py():
    datadir = DATA_DIR
    paths = (('a', 'c', 'd.py'),)
    expected = sorted(datadir / Path(*path) for path in paths)
    results = sorted(find_modules(datadir / 'a' / 'c' / 'd.py'))
    assert expected == results


def test_finding_module_py_dot_py_using_dots():
    datadir = DATA_DIR
    paths = (('a', 'py.py'),)
    expected = sorted(datadir / Path(*path) for path in paths)
    results = sorted(find_modules(datadir / 'a' / 'py.py'))
    assert expected == results


def test_finding_modules_py_dot_py_using_slashes():
    datadir = DATA_DIR
    results = sorted(find_modules(datadir / 'a' / 'py'))
    assert [] == results


def test_finding_modules_py_dot_py_using_slashes_with_full_filename():
    datadir = DATA_DIR
    paths = (('a', 'py.py'),)
    expected = sorted(datadir / Path(*path) for path in paths)
    results = sorted(find_modules(datadir / 'a' / 'py.py'))
    assert expected == results
