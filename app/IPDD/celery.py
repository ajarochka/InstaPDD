from __future__ import absolute_import
from django.apps import apps
from celery import Celery
import os

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IPDD.settings')

app = Celery('ipdd')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])
# app.autodiscover_tasks()

# app.conf.task_default_queue = 'ipdd'/opt/ipdd/venv/bin/celery --app=IPDD worker
