"""Implementation of the WorkDB."""

import contextlib
import os
import sqlite3
from enum import Enum
from io import StringIO

import kfg.yaml

from .config import Config
from .testing.test_runner import TestOutcome
from .work_item import WorkItem, WorkResult
from .worker import WorkerOutcome


class WorkDB:
    """WorkDB is the database that keeps track of mutation testing work progress.

    Essentially, there's a row in the DB for each mutation that needs to be
    executed in some run. These initially start off with no results, and
    results are added as they're completed.
    """
    class Mode(Enum):
        "Modes in which a WorkDB may be opened."

        # Open existing files, creating if necessary
        create = 1

        # Open only existing files, failing if it doesn't exist
        open = 2

    def __init__(self, path, mode):
        """Open a DB in file `path` in mode `mode`.

        Args:
          path: The path to the DB file.
          mode: The mode in which to open the DB. See the `Mode` enum for
            details.

        Raises:
          FileNotFoundError: If `mode` is `Mode.open` and `path` does not
            exist.
        """

        if (mode == WorkDB.Mode.open) and (not os.path.exists(path)):
            raise FileNotFoundError(
                'Requested file {} not found'.format(path))

        self._path = path
        self._conn = sqlite3.connect(path)

        self._init_db()

    def close(self):
        """Close the database."""
        self._conn.close()

    @property
    def name(self):
        """A name for this database.

        Derived from the constructor arguments.
        """
        return self._path

    def set_config(self, config, timeout):
        """Set (replace) the configuration for the session.

        Args:
          config: Configuration object
          timeout: The timeout for tests.
        """
        with self._conn:
            self._conn.execute("DELETE FROM config")
            self._conn.execute('INSERT INTO config VALUES(?, ?)',
                               (kfg.yaml.serialize_config(config),
                                timeout))

    def get_config(self):
        """Get the work parameters (if set) for the session.

        Returns: a tuple of `(config, timeout)`.

        Raises:
          ValueError: If is no config set for the session.
        """
        rows = list(self._conn.execute("SELECT * FROM config"))
        if not rows:
            raise ValueError("work-db has no config")
        config_str, timeout = rows[0]

        return (kfg.yaml.load_config(StringIO(config_str),
                                     config=Config()),
                timeout)

    @property
    def work_items(self):
        """An iterable of all of WorkItems in the db.

        This includes both WorkItems with and without results.
        """
        cur = self._conn.cursor()
        rows = cur.execute("SELECT * FROM work_items")
        return (WorkItem(*r) for r in rows)

    @property
    def num_work_items(self):
        """The number of work items."""
        count = self._conn.execute("SELECT COUNT(*) FROM work_items")
        return list(count)[0][0]

    def add_work_items(self, work_items):
        """Add a sequence of WorkItems.

        Args:
          work_items: An iterable of WorkItems.
        """
        with self._conn:
            for item in work_items:
                # TODO: Is there an "insert many" option?
                self._conn.execute(
                    '''
                    INSERT INTO work_items
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (str(item.module_path),
                     item.operator_name,
                     item.occurrence,
                     item.line_number,
                     item.col_offset,
                     item.job_id))

    def clear(self):
        """Clear all work items from the session.

        This removes any associated results as well.
        """
        with self._conn:
            self._conn.execute('DELETE FROM work_items')

    @property
    def results(self):
        "An iterable of all `(job-id, WorkResult)`s."
        cur = self._conn.cursor()
        rows = cur.execute("SELECT * FROM results")
        for row in rows:
            yield ((row['job_id'],
                    WorkResult(
                        worker_outcome=WorkerOutcome(row['worker_outcome']),
                        data=row['data'],
                        test_outcome=TestOutcome(row['test_outcome']),
                        diff=row['diff'])))

    @property
    def num_results(self):
        """The number of results."""
        count = self._conn.execute("SELECT COUNT(*) FROM work_items")
        return list(count)[0][0]

    def add_result(self, job_id, result):
        """Add a sequence of WorkResults to the db.

        Args:
          result: An iterable of `(job-id, WorkResult)`s.

        Raises:
           KeyError: If there is no work-item with a matching job-id.
           KeyError: If there is an existing result with a matching job-id.
        """
        with self._conn:
            try:
                self._conn.execute(
                    '''
                    INSERT INTO results
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (str(result.data),
                     None if result.test_outcome is None else result.test_outcome.value,
                     result.worker_outcome.value,  # should never be None
                     result.diff, 
                     job_id))
            except sqlite3.IntegrityError as exc:
                raise KeyError('Can not add result with job-id {}'.format(job_id)) from exc

    @property
    def pending_work_items(self):
        "Iterable of all pending work items."
        pending = self._conn.execute("SELECT * FROM work_items WHERE job_id NOT IN (SELECT job_id FROM results)")
        return (WorkItem(*p) for p in pending)

    # @property
    # def num_pending_work_items(self):
    #     "The number of pending WorkItems in the session."
    #     count = self._conn.execute("SELECT COUNT(*) FROM work_items WHERE job_id NOT IN (SELECT job_id FROM results)")
    #     return count[0][0]

    def _init_db(self):
        with self._conn:
            self._conn.row_factory = sqlite3.Row

            self._conn.execute("PRAGMA foreign_keys = 1")

            self._conn.execute('''
            CREATE TABLE IF NOT EXISTS work_items
            (module_path text,
             operator text,
             occurrence int,
             line_number int,
             col_offset int,
             job_id text primary key)
            ''')

            self._conn.execute('''
            CREATE TABLE IF NOT EXISTS results
            (data text,
             test_outcome text,
             worker_outcome text,
             diff text,
             job_id text primary key,
             FOREIGN KEY(job_id) REFERENCES work_items(job_id)
            )
            ''')

            self._conn.execute('''
            CREATE TABLE IF NOT EXISTS config
            (config text,
             timeout real)
            ''')


@contextlib.contextmanager
def use_db(path, mode=WorkDB.Mode.create):
    """
    Open a DB in file `path` in mode `mode` as a context manager.

    On exiting the context the DB will be automatically closed.

    Args:
      path: The path to the DB file.
      mode: The mode in which to open the DB. See the `Mode` enum for
        details.

    Raises:
      FileNotFoundError: If `mode` is `Mode.open` and `path` does not
        exist.
    """
    database = WorkDB(path, mode)
    try:
        yield database
    finally:
        database.close()
