"""Central location for celery-specific stuff."""

from celery import Celery

_app = None


def app(config=None):
    global _app

    if config is not None:
        _app = Celery(
            'cosmic-ray-celery-executor',
            broker='amqp://',
            backend='amqp://')

        _app.conf.CELERY_ACCEPT_CONTENT = ['json']
        _app.conf.CELERY_TASK_SERIALIZER = 'json'
        _app.conf.CELERY_RESULT_SERIALIZER = 'json'

    return _app

# This will remove all pending work from the queue. We need to do this when we
# shut down during exec:
#
#     cosmic_ray.celery.app.control.purge()
