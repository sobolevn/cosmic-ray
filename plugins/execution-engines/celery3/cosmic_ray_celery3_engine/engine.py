"Implementation of the celery3 execution engine plugin."

from cosmic_ray.execution.execution_engine import ExecutionEngine
from cosmic_ray.work_item import WorkItem

from .app import APP
from .worker import worker, execute_work_items


class CeleryExecutionEngine(ExecutionEngine):
    "The celery3 execution engine."
    def __call__(self, timeout, pending_work, config, on_task_complete):
        purge_queue = config['execution-engine'].get('purge-queue', True)

        try:
            job = worker(
                work_item.module_path, 
                cosmic_ray.plugins.get_operator(work_item.operator_name),
                work_item.occurrence,
                config['test-command'],
                timeout)

            result = job.apply_async()
            result.get(callback=on_task_complete)
        finally:
            if purge_queue:
                APP.control.purge()
