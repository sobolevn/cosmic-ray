"Support for running tests in a subprocess."

import subprocess
import sys
import traceback

from cosmic_ray.work_item import TestOutcome


# TODO: We can probably lift this module out of the subpackage and remove the
# subpackage.


def run_tests(command, timeout=None):
    """Run test command in a subprocess.

    If the command exits with status 0, then we assume that all tests passed. If
    it exits with any other code, we assume a test failed. If the call to launch
    the subprocess throws an exception, we consider the test 'incompetent'.

    Tests which time out are considered 'incompetent' as well.

    Args: 
        command (str): The command to execute.
        timeout (number): The maximum number of seconds to allow the tests to run.

    Return: A tuple `(TestOutcome, output)` where the `output` is a string
        containing the output of the command.
    """
    try:
        command = command.format(python_executable=sys.executable)
        proc = subprocess.run(command.split(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              timeout=timeout)

        outcome = TestOutcome.SURVIVED if proc.returncode == 0 else TestOutcome.KILLED

        return (outcome, proc.stdout.decode())

    except Exception:
        return (TestOutcome.INCOMPETENT, traceback.format_exc())

