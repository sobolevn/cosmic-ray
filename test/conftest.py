from pathlib import Path

import pytest


@pytest.fixture
def tmpdir_path(tmpdir):
    """A temporary directory as a pathlib.Path.
    """
    return Path(str(tmpdir))    