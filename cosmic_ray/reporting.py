"""Functions for calculate certain kinds of reports.
"""

from cosmic_ray.testing.test_runner import TestOutcome
from cosmic_ray.worker import WorkerOutcome


def _print_item(work_item, result, full_report):
    if result is None:
        yield 'job ID {}:::{}'.format(work_item.job_id, work_item.module_path)
        return

    ret_val = [
        'job ID {}:{}:{}:{}'.format(
            work_item.job_id,
            result.worker_outcome,
            result.test_outcome,
            work_item.module_path),
        # TODO: Include command line here. We'll create new support for constructing these.
    ]

    if result.test_outcome in {TestOutcome.KILLED, TestOutcome.INCOMPETENT} and not full_report:
        ret_val = []
    elif result.worker_outcome == WorkerOutcome.SKIPPED and not full_report:
        ret_val = []
    elif result.worker_outcome in {WorkerOutcome.NORMAL,
                                   WorkerOutcome.EXCEPTION}:
        ret_val += result.output

        if work_item.diff is not None:
            ret_val += work_item.diff

    # for presentation purposes only
    if ret_val:
        ret_val.append('')

    return ret_val


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


def create_report(records, show_pending, full_report=False):
    """Generate the lines of a simple report.

    Args:
      records: An iterable of (`WorkItem`, `WorkResult`)s.
      show_pending: Show output for records which are pending.
      full_report: Whether to report on mutants that were killed.
    """
    total_jobs = 0
    pending_jobs = 0
    kills = 0
    for item, result in records:
        total_jobs += 1
        if result is None:
            pending_jobs += 1
        elif is_killed(result):
            kills += 1

        if (result is not None) or show_pending:
            yield from _print_item(item, result, full_report)

    completed_jobs = total_jobs - pending_jobs

    yield 'total jobs: {}'.format(total_jobs)

    if completed_jobs > 0:
        yield 'complete: {} ({:.2f}%)'.format(
            completed_jobs, completed_jobs / total_jobs * 100)
        yield 'survival rate: {:.2f}%'.format(
            (1 - kills / completed_jobs) * 100)
    else:
        yield 'no jobs completed'


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
