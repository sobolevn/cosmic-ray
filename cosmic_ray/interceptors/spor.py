"""An interceptor that uses spor metadata to determine when specific mutations
should be skipped.
"""
import logging

from spor.repository import open_repository

from cosmic_ray.work_item import WorkerOutcome, WorkResult

log = logging.getLogger()


def intercept(work_db):
    """Look for WorkItems in `work_db` that should not be mutated due to spor metadata.

    For each WorkItem, find anchors for the item's file/line/columns. If an
    anchor exists with metadata containing `{mutate: False}` then the WorkItem
    is marked as SKIPPED.
    """
    # TODO: TEMPORARY! Remove this return once we get this working again.
    return

    for item in work_db.work_items:

        try:
            repo = open_repository(item.module_path)
        except ValueError:
            log.info('No spor repository for %s', item.module_path)
            continue

        for _, anchor in repo.items():
            metadata = anchor.metadata

            # TODO: Need to figure out item's offset from its line number. Then need to compare that with anchor.
            if (_offset(item) in anchor) and not metadata.get('mutate', True):
                log.info('spor skipping %s %s %s',
                         item.job_id,
                         item.operator_name,
                         item.occurrence)

                work_db.add_result(
                    item.job_id,
                    WorkResult(
                        output=None,
                        test_outcome=None,
                        diff=None,
                        worker_outcome=WorkerOutcome.SKIPPED))
