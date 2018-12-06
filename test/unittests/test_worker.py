from pathlib import Path

from cosmic_ray.operators import boolean_replacer
from cosmic_ray.plugins import get_test_runner
from cosmic_ray.work_item import WorkItem
from cosmic_ray.worker import worker, WorkerOutcome

from path_utils import DATA_DIR, excursion, extend_path


def test_no_test_return_value():
    with extend_path(DATA_DIR), excursion(DATA_DIR):
        test_runner = get_test_runner("unittest", ".")
        result = worker(Path("a/b.py"), boolean_replacer.ReplaceTrueFalse,
                        100, test_runner)
        expected = WorkItem(worker_outcome=WorkerOutcome.NO_TEST)
        assert result == expected
