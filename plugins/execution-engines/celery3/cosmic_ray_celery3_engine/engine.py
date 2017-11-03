import celery
from cosmic_ray.execution.execution_engine import ExecutionEngine
from cosmic_ray.work_record import WorkRecord
from cosmic_ray.worker import worker_process

from .app import app


# pylint: disable=too-few-public-methods
class CeleryExecutionEngine(ExecutionEngine):
    def __init__(self, args):
        self.app = celery.Celery(
            'cosmic-ray-celery-executor',
            broker=args.get('broker', 'amqp://'),
            backend=args.get('backend', 'amqp://'))

        self.app.conf.CELERY_ACCEPT_CONTENT = ['json']
        self.app.conf.CELERY_TASK_SERIALIZER = 'json'
        self.app.conf.CELERY_RESULT_SERIALIZER = 'json'

        class Task(self.app.Task):
            def run(self, work_record, timeout, config):
                return worker_process(work_record, timeout, config)

        self.worker_task = self.app.tasks[Task.name]

    def __call__(self, timeout, pending_work, config):
        purge_queue = config['execution-engine'].get('purge-queue', True)

        try:
            results = celery.group(
                self.worker_task.delay(work_record,
                                       timeout,
                                       config)
                for work_record in pending_work)

            for result in results:
                yield WorkRecord(result.get())
        finally:
            if purge_queue:
                app.control.purge()
