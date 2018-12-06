from kfg.config import Config
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


def test_num_work_items(work_db):
    work_db.add_work_items([
        WorkItem('path', 'operator', 0, 0, 0, 'job_id_{}'.format(idx))
        for idx in range(10)
    ])
    assert work_db.num_work_items == 10


def test_clear_removes_work_items(work_db):
    work_db.add_work_items([
        WorkItem('path', 'operator', 0, 0, 0, 'job_id_{}'.format(idx))
        for idx in range(10)
    ])
    work_db.clear()
    assert work_db.num_work_items == 0


def test_clear_work_items_removes_results(work_db):
    work_db.add_work_items([
        WorkItem('path', 'operator', 0, 0, 0, 'job_id_{}'.format(idx))
        for idx in range(10)
    ])


def test_work_items(work_db):
    original = [
        WorkItem('path_{}'.format(idx),
                 'operator_{}'.format(idx),
                 idx,
                 idx,
                 idx,
                 'job_id_{}'.format(idx))
        for idx in range(10)
    ]
    work_db.add_work_items(original)

    actual = list(work_db.work_items)

    assert actual == original


def test_results(work_db):
    work_db.add_work_items([
        WorkItem('path_{}'.format(idx),
                 'operator_{}'.format(idx),
                 idx,
                 idx,
                 idx,
                 'job_id_{}'.format(idx))
        for idx in range(10)])

    original = [
        ('job_id_{}'.format(idx),
         WorkResult(
             data='data_{}'.format(idx),
             test_outcome=TestOutcome.KILLED,
             worker_outcome=WorkerOutcome.NORMAL,
             diff='diff_{}'.format(idx)))
            for idx in range(10)]

    for result in original:
        work_db.add_result(*result)

    actual = list(work_db.results)

    assert actual == original


def test_set_config(work_db):
    config = Config()
    config['ui', 'font-color'] = 'blue'
    work_db.set_config(config, 100.234)


def test_get_config_raises_ValueError_with_no_config(work_db):
    with pytest.raises(ValueError):
        work_db.get_config()


def test_get_config_returns_correct_config(work_db):
    config = Config()
    config['ui', 'font-color'] = 'blue'
    timeout = 100.234
    work_db.set_config(config, timeout)

    actual_config, actual_timeout = work_db.get_config()
    assert actual_config['ui', 'font-color'] == 'blue'
    assert actual_timeout == timeout
