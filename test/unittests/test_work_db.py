import pytest

from cosmic_ray.testing.test_runner import TestOutcome
from cosmic_ray.worker import WorkerOutcome
from cosmic_ray.work_db import use_db, WorkDB
from cosmic_ray.work_item import WorkItem, WorkResult


@pytest.fixture
def work_db():
    with use_db(':memory:', WorkDB.Mode.create) as db:
        yield db


def test_empty_db_has_no_pending_jobs(work_db):
    assert len(list(work_db.pending_work_items)) == 0


def test_find_pending_job(work_db):
    item = WorkItem('path', 'operator', 0, 0, 0, 'job_id')
    work_db.add_work_items([item])
    pending = list(work_db.pending_work_items)
    assert pending == [item]


def test_jobs_with_results_are_not_pending(work_db):
    work_db.add_work_items([
        WorkItem('path', 'operator', 0, 0, 0, 'job_id')
    ])
    work_db.add_result(
        'job_id',
        WorkResult('data',
                   TestOutcome.KILLED,
                   WorkerOutcome.NORMAL,
                   'diff'))
    assert not list(work_db.pending_work_items)


def test_add_result_throws_KeyError_if_no_matching_work_item(work_db):
    with pytest.raises(KeyError):
        work_db.add_result(
            'job_id',
            WorkResult('data',
                       TestOutcome.KILLED,
                       WorkerOutcome.NORMAL,
                       'diff'))


def test_add_result_throws_KeyError_if_result_exists(work_db):
    work_db.add_work_items([
        WorkItem('path', 'operator', 0, 0, 0, 'job_id')
    ])

    work_db.add_result(
        'job_id',
        WorkResult('data',
                   TestOutcome.KILLED,
                   WorkerOutcome.NORMAL,
                   'diff'))

    with pytest.raises(KeyError):
        work_db.add_result(
            'job_id',
            WorkResult('data',
                       TestOutcome.KILLED,
                       WorkerOutcome.NORMAL,
                       'diff'))
