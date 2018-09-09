"""This is the body of the low-level worker tool.

A worker is intended to run as a process that imports a module, mutates it in
one location with one operator, runs the tests, reports the results, and dies.
"""

import difflib
import logging
import subprocess
import sys
import traceback

import cosmic_ray.compat.json
from cosmic_ray.config import serialize_config
from cosmic_ray.importing import using_mutant
from cosmic_ray.testing.test_runner import TestOutcome
from cosmic_ray.util import StrEnum
from cosmic_ray.work_item import WorkItem, WorkItemJsonDecoder


try:
    import typing      # the typing module does some fancy stuff at import time
                       # which we shall not do twice... by loading it here,
                       # preserve_modules does not delete it and therefore
                       # fancy stuff happens only once
except ImportError:
    pass

log = logging.getLogger()


class WorkerOutcome(StrEnum):
    """Possible outcomes for a worker.
    """
    NORMAL = 'normal'       # The worker exited normally, producing valid output
    EXCEPTION = 'exception' # The worker exited with an exception
    ABNORMAL = 'abnormal'   # The worker did not exit normally or with an exception (e.g. a segfault)
    NO_TEST = 'no-test'     # The worker had no test to run
    TIMEOUT = 'timeout'     # The worker timed out
    SKIPPED = 'skipped'     # The job was skipped (worker was not executed)


def worker(module_name,
           operator_class,
           occurrence,
           test_runner):
    """Mutate the OCCURRENCE-th site for OPERATOR_CLASS in MODULE_NAME, run the
    tests, and report the results.

    This is fundamentally the single-mutation-and-test-run process
    implementation.

    There are three high-level ways that a worker can finish. First, it could
    fail exceptionally, meaning that some uncaught exception made its way from
    some part of the operation to terminate the function. This function will
    intercept all exceptions and return it in a non-exceptional structure.

    Second, the mutation testing machinery may determine that there is no
    OCCURENCE-th instance for OPERATOR_NAME in the module under test. In this
    case there is no way to report a test result (i.e. killed, survived, or
    incompetent) so a special value is returned indicating that no mutation is
    possible.

    Finally, and hopefully normally, the worker will find that it can run a
    test. It will do so and report back the result - killed, survived, or
    incompetent - in a structured way.

    Returns: a WorkItem

    Raises: This will generally not raise any exceptions. Rather, exceptions
        will be reported using the 'exception' result-type in the return value.
    """
    try:
        with using_mutant(module_name, operator_class, occurrence) as context:
            item = test_runner()

            if not context.activation_record:
                return WorkItem(
                    worker_outcome=WorkerOutcome.NO_TEST)

            item.update({
                'diff': _generate_diff(context),
                'worker_outcome': WorkerOutcome.NORMAL
            })
            item.update(context.activation_record)
            return item

    except Exception:  # noqa # pylint: disable=broad-except
        return WorkItem(
            data=traceback.format_exception(*sys.exc_info()),
            test_outcome=TestOutcome.INCOMPETENT,
            worker_outcome=WorkerOutcome.EXCEPTION)


def _generate_diff(context):
    """Generate a source diff to visualize how the mutation
    operator has changed the code.
    """
    module_diff = ["--- mutation diff ---"]
    for line in difflib.unified_diff(
            context.module_source.split('\n'),
            context.modified_source.split('\n'),
            fromfile="a" + context.module_source_file,
            tofile="b" + context.module_source_file,
            lineterm=""):
        module_diff.append(line)
    return module_diff


def worker_process(work_item,
                   timeout,
                   config):
    """Run `cosmic-ray worker` in a subprocess and return the results,
    passing `config` to it via stdin.

    Returns: An updated WorkItem

    """
    # The work_item param may come as just a dict (e.g. if it arrives over
    # celery), so we reconstruct a WorkItem to make it easier to work with.
    work_item = WorkItem(work_item)

    command = 'cosmic-ray worker {module} {operator} {occurrence}'.format(
        **work_item)

    log.info('executing: %s', command)

    proc = subprocess.Popen(command.split(),
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
    config_string = serialize_config(config)
    try:
        outs, _ = proc.communicate(input=config_string, timeout=timeout)
        result = cosmic_ray.compat.json.loads(outs, cls=WorkItemJsonDecoder)
        work_item.update({
            k: v
            for k, v
            in result.items()
            if v is not None
        })
    except subprocess.TimeoutExpired as exc:
        work_item.worker_outcome = WorkerOutcome.TIMEOUT
        work_item.data = exc.timeout
        proc.kill()
    except cosmic_ray.compat.json.JSONDecodeError as exc:
        work_item.test_outcome = TestOutcome.INCOMPETENT
        work_item.worker_outcome = WorkerOutcome.ABNORMAL
        work_item.data = traceback.format_exception(*sys.exc_info())

    work_item.command_line = command
    return work_item
