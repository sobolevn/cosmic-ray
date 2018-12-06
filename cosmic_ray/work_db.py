"""Implementation of the WorkDB."""

import contextlib
from io import StringIO
import os
import sqlite3
from enum import Enum

# This db may well not scale very well. We need to be ready to switch it out
# for something quicker if not. But for now it's *very* convenient.
import tinydb
import kfg.yaml

from .config import Config
from .work_item import WorkItem


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

    def _init_db(self):
        with self._conn:
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
            job_id text primary key)
            ''')

            self._conn.execute('''
            CREATE TABLE IF NOT EXISTS config
            (config text)
            ''')

    def close(self):
        """Close the database."""
        self._conn.close()

    @property
    def name(self):
        """A name for this database.

        Derived from the constructor arguments.
        """
        return self._path

    @property
    def pending_work_items(self):
        pending = self._conn.execute("SELECT * FROM work_items WHERE job_id NOT IN (SELECT job_id FROM results)")
        return (WorkItem(*p) for p in pending)

    # def set_config(self, config, timeout):
    #     """Set (replace) the configuration for the session.

    #     Args:
    #       config: Configuration object
    #       timeout: The timeout for tests.
    #     """
    #     table = self._config
    #     table.purge()
    #     table.insert({
    #         'config': kfg.yaml.serialize_config(config),
    #         'timeout': timeout,
    #     })

    # def get_config(self):
    #     """Get the work parameters (if set) for the session.

    #     Returns: a tuple of `(config, timeout)`.

    #     Raises:
    #       ValueError: If is no config set for the session.
    #     """
    #     table = self._config

    #     try:
    #         record = table.all()[0]
    #     except IndexError:
    #         raise ValueError('work-db has no config')

    #     return (kfg.yaml.load_config(StringIO(record['config']), config=Config()),
    #             record['timeout'])

    def add_work_items(self, work_items):
        """Add a sequence of WorkItems.

        Args:
          work_items: An iterable of WorkItems.
        """
        with self._conn:
            for item in work_items:
                # TODO: Is there an "insert many" option?
                self._conn.execute('''
                INSERT INTO work_items
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                                   (str(item.module_path),
                                    item.operator,
                                    item.occurrence,
                                    item.line_number,
                                    item.col_offset,
                                    item.job_id))

    def add_result(self, job_id, result):
        """Add a sequence of WorkResults to the db.

        Args:
          result: An iterable of `(job-id, WorkResult)`s.

        Raises:
           KeyError: If there is no work-item with a matching job-id.
           KeyError: If there is an existing result with a matching job-id.
        """
        with self._conn:
            # TODO: Can we design the table such that the database itself will enforce this constraint?
            count = self._conn.execute(
                '''
                SELECT COUNT(*) FROM work_items WHERE job_id == ?
                ''',
                (job_id,))

            if list(count)[0][0] == 0:
                raise KeyError('No WorkItem with job-id {}'.format(job_id))

            try:
                self._conn.execute(
                    '''
                    INSERT INTO results
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (str(result.data),
                     result.test_outcome,
                     result.worker_outcome,
                     result.diff,
                     job_id))
            except sqlite3.IntegrityError as exc:
                raise KeyError('Result with job-id {} already exists'.format(job_id)) from exc

    # def clear_work_items(self):
    #     """Clear all work items from the session.

    #     This removes any associated results as well.
    #     """
    #     # TODO: Clear results as well.
    #     self._work_items.purge()

    # @property
    # def work_items(self):
    #     """The sequence of WorkItems in the session.

    #     This include both complete and incomplete items.

    #     Each work item is a dict with the keys `module-name`, `op-name`, and
    #     `occurrence`. Items with results will also have the keys `results-type`
    #     and `results-data`.
    #     """
    #     return (WorkItem(**r) for r in self._work_items)

    # @property
    # def num_work_items(self):
    #     """The number of WorkItems."""
    #     return len(self._work_items)

    # def _remove_update_work_item(self, work_item):
    #     """Updates an existing WorkItem by job_id.

    #     Args:
    #         work_item: A WorkItem representing the new state of a job.

    #     Raises:
    #         KeyError: If there is no existing record with the same job_id.
    #     """
    #     self._work_items.update(
    #         work_item.as_dict(),
    #         tinydb.Query().job_id == work_item.job_id
    #     )

    # @property
    # def num_pending_work_items(self):
    #     """The number of pending WorkItems in the session."""
    #     return len(self._pending)

    # def add_result(self, work_result):
    #     """Add a WorkResult.

    #     Args:
    #       work_result: A WorkResult.

    #         #     """
    #     table = self._work_items
    #     work_item = tinydb.Query()
    #     work_items = self._work_items.search(work_item.job_id == work_result.job_id)

    #     self._work_results.insert(work_result.as_dict())

    #     self._work_items.insert_multiple(work_item.as_dict() for work_item in work_items)


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
    except Exception:
        raise
    finally:
        database.close()
