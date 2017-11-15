import io
import logging

import pytest

import cosmic_ray.progress as prog


log = logging.getLogger()


@pytest.fixture
def progress_handler():
    handler = prog.ProgressLogHandler()
    log.addHandler(handler)
    yield handler
    log.removeHandler(handler)
    handler.close()


def test_progress_logging_message_is_correct(progress_handler):
    log.log(prog.PROGRESS, "test%s", 42)

    stream = io.StringIO()
    prog.report_progress(stream)
    assert stream.getvalue() == "test42\n"


def test_progress_logging_to_non_root_logger(progress_handler):
    sublog = logging.getLogger('crtest')
    sublog.log(prog.PROGRESS, "test")

    stream = io.StringIO()
    prog.report_progress(stream)
    assert stream.getvalue() == "test\n"


def test_no_progress_report_without_handler():
    log.log(prog.PROGRESS, "test")
    stream = io.StringIO()
    prog.report_progress(stream)
    assert stream.getvalue() == ""
