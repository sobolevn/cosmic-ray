"Base test-runner implementation details."

import abc
import sys
import subprocess
import traceback

from cosmic_ray.util import StrEnum
from cosmic_ray.work_item import WorkItem


class TestOutcome(StrEnum):
    """A enum of the possible outcomes for any mutant test run.
    """
    SURVIVED = 'survived'
    KILLED = 'killed'
    INCOMPETENT = 'incompetent'


def run_tests(command, timeout=0):
    """Run test command in a subprocess.

    If the command exits with status 0, then we assume that all tests passed. If
    it exits with any other code, we assume a test failed. If the call to launch
    the subprocess throws an exception, we consider the test 'incompetent'.

    Args: command (str): The command to execute.

    Return: A tuple `(TestOutcome, output)` where the `output` is a string
        containing the output of the command.
    """
    try:
        completed_process = subprocess.run(command.split(),
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT,
                                           timeout=timeout)
        if completed_process.returncode == 0:
            return (TestOutcome.SURVIVED, completed_process.stdout)
        return (TestOutcome.KILLED, completed_process.stdout)
    except Exception:
        return (TestOutcome.INCOMPETENT, traceback.format_exc())


class TestRunner(metaclass=abc.ABCMeta):
    """Specifies the interface for test runners in the system.

    There are many ways to run unit tests in Python, and each method
    supported by Cosmic Ray should be provided by a TestRunner
    implementation.
    """

    def __init__(self, test_args):
        self._test_args = test_args

    @property
    def test_args(self):
        """The arguments for the test runner.

        This is typically just a string, but it's whatever was passed to the
        `TestRunner` initializer.
        """
        return self._test_args

    @abc.abstractmethod
    def _run(self):
        """Run all of the tests and return the results.

        The results are returned as a (success, result)
        tuple. `success` is a boolean indicating if the tests
        passed. `result` is any object that is appropriate to provide
        more information about the success/failure of the tests.
        """
        pass

    def __call__(self):
        """Call `_run()` and return a `WorkItem` with the results.

        Returns: A tuple of `(TestOutcome, data)`.
        """
        try:
            test_result = self._run()
            if test_result[0]:
                return (TestOutcome.SURVIVED, test_result[1])
            return (TestOutcome.KILLED, test_result[1])
        except Exception:  # pylint: disable=broad-except
            return (TestOutcome.INCOMPETENT,
                    traceback.format_exception(*sys.exc_info()))
