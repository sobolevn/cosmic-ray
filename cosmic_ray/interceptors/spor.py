"""An interceptor that uses spor metadata to determine when specific mutations
should be skipped.
"""
import logging

from spor.repo import find_anchors

from cosmic_ray.work_item import WorkerOutcome, WorkResult

log = logging.getLogger()


def intercept(work_db):
    """Look for WorkItems in `work_db` that should not be mutated due to spor metadata.

    For each WorkItem, find anchors for the item's file/line/columns. If an
    anchor exists with metadata containing `{mutate: False}` then the WorkItem
    is marked as SKIPPED.
    """
    for item in work_db.work_items:
        try:
            anchors = tuple(find_anchors(item.module_path))
        except ValueError:
            log.info('No spor repository for %s', item.module_path)
            continue

        for anchor in anchors:
            metadata = anchor.metadata
            if item.line_number == anchor.line_number and not metadata.get('mutate', True):
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
