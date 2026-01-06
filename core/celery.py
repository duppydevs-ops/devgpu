from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from kombu import Exchange, Queue

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.task_queues = (
    Queue("queue1", Exchange("queue1"), routing_key="queue1"),
    Queue("queue2", Exchange("queue2"), routing_key="queue2"),
    Queue("queue3", Exchange("queue3"), routing_key="queue3"),
)

app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()
