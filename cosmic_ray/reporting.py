"""Functions for calculate certain kinds of reports.
"""

from cosmic_ray.testing.test_runner import TestOutcome
from cosmic_ray.worker import WorkerOutcome


def is_killed(result):
    """Determines if a WorkItem should be considered "killed".

    Args:
        result: A `WorkResult`

    Returns: A bool indicating if the result should be considered a kill.
    """
    if result.worker_outcome == WorkerOutcome.SKIPPED:
        return True
    elif result.worker_outcome in {WorkerOutcome.ABNORMAL, WorkerOutcome.NORMAL}:
        if result.test_outcome == TestOutcome.KILLED:
            return True
        if result.test_outcome == TestOutcome.INCOMPETENT:
            return True
    return False

def survival_rate(work_db):
    """Calcuate the survival rate for the results in a WorkDB.
    """
    total_jobs = work_db.num_work_items
    pending_jobs = total_jobs - work_db.num_results
    kills = sum(is_killed(r) for _, r in work_db.results)

    completed_jobs = total_jobs - pending_jobs

    if not completed_jobs:
        rate = 0
    else:
        rate = (1 - kills / completed_jobs) * 100

    return rate
