"""This is the body of the low-level worker tool.
"""

from contextlib import contextmanager
import difflib
import traceback

from cosmic_ray.ast import get_ast
import cosmic_ray.compat.json
import cosmic_ray.mutating
import cosmic_ray.plugins
from cosmic_ray.testing.test_runner import run_tests
from cosmic_ray.work_item import TestOutcome, WorkerOutcome, WorkResult


# TODO: Is this still necessary?
try:
    import typing      # the typing module does some fancy stuff at import time
    # which we shall not do twice... by loading it here,
    # preserve_modules does not delete it and therefore
    # fancy stuff happens only once
except ImportError:
    pass


def worker(module_path,
           operator_name,
           occurrence,
           test_command,
           timeout):
    """Mutate the OCCURRENCE-th site for OPERATOR_NAME in MODULE_PATH, run the
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

    Args:
        module_name: The path to the module to mutate
        operator_name: The name of the operator plugin to use
        occurrence: The occurrence of the operator to apply
        test_command: The command to execute to run the tests
        timeout: The maximum amount of time to let the tests run

    Returns: A WorkResult

    Raises: This will generally not raise any exceptions. Rather, exceptions
        will be reported using the 'exception' result-type in the return value.

    """
    try:
        operator_class = cosmic_ray.plugins.get_operator(operator_name)

        with _apply_mutation(module_path, operator_class(), occurrence) as (mutation_applied, diff):
            if not mutation_applied:
                return WorkResult(
                    worker_outcome=WorkerOutcome.NO_TEST)

            test_outcome, output = run_tests(test_command, timeout)

            return WorkResult(
                output=output.decode(),
                diff='\n'.join(diff),
                test_outcome=test_outcome,
                worker_outcome=WorkerOutcome.NORMAL)

    except Exception:  # noqa # pylint: disable=broad-except
        return WorkResult(
            output=traceback.format_exc(),
            test_outcome=TestOutcome.INCOMPETENT,
            worker_outcome=WorkerOutcome.EXCEPTION)


@contextmanager
def _apply_mutation(module_path, operator, occurrence):
    # TODO: how do we communicate the python version?
    module_ast = get_ast(module_path, python_version="3.6")
    source = module_ast.get_code()

    visitor = cosmic_ray.mutating.MutationVisitor(occurrence,
                                                  operator)
    mutated_ast = visitor.walk(module_ast)
    modified_source = mutated_ast.get_code()

    # generate a source diff to visualize how the mutation
    # operator has changed the code
    module_diff = ["--- mutation diff ---"]
    for line in difflib.unified_diff(source.split('\n'),
                                     modified_source.split('\n'),
                                     fromfile="a" + str(module_path),
                                     tofile="b" + str(module_path),
                                     lineterm=""):
        module_diff.append(line)

    try:
        with module_path.open(mode='wt', encoding='utf-8') as handle:
            handle.write(modified_source)
        yield visitor.activation_record is not None, module_diff
    finally:
        with module_path.open(mode='wt', encoding='utf-8') as handle:
            handle.write(source)

