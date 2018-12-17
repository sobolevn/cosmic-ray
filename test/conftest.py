from pathlib import Path
import sys

import pytest


@pytest.fixture
def tmpdir_path(tmpdir):
    """A temporary directory as a pathlib.Path.
    """
    return Path(str(tmpdir))    


@pytest.fixture
def session(tmpdir_path):
    """A temp session file (pathlib.Path)
    """
    return tmpdir_path / 'cr-session.sqlite'

@pytest.fixture
def python_version():
    return "{}.{}".format(sys.version_info.major, sys.version_info.minor)

