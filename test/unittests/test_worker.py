from pathlib import Path

from cosmic_ray.operators import boolean_replacer
from cosmic_ray.plugins import get_test_runner
from cosmic_ray.work_item import WorkResult
from cosmic_ray.worker import worker, WorkerOutcome

from path_utils import excursion


def test_no_test_return_value(data_dir):
    with excursion(data_dir):
        test_runner = get_test_runner("unittest", ".")
        result = worker(Path("a/b.py"), boolean_replacer.ReplaceTrueWithFalse,
                        100, test_runner)
        expected = WorkResult(
            output=None,
            test_outcome=None,
            diff=None,
            worker_outcome=WorkerOutcome.NO_TEST)
        assert result == expected
