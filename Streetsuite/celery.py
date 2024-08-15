from __future__ import absolute_import , unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
import logging.config
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE','Streetsuite.settings')

## instnce of celery application ##
app = Celery('Streetsuite')

app.config_from_object('django.conf:settings',namespace='CELERY')

app.autodiscover_tasks()

# def setup_celery_logging(**kwargs):
#     logging.config.dictConfig(settings.LOGGING)