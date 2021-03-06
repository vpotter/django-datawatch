# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger
from celery.schedules import crontab
from celery.task.base import PeriodicTask
from django.conf import settings

from django_datawatch.backends import synchronous
from django_datawatch.defaults import defaults
from django_datawatch.datawatch import Scheduler

logger = get_task_logger(__name__)


@shared_task
def django_datawatch_enqueue(slug, *args, **kwargs):
    logger.debug('enqueuing checks for %s', slug)
    synchronous.Backend().enqueue(slug)


@shared_task
def django_datawatch_refresh(slug, *args, **kwargs):
    logger.debug('refreshing check results for %s', slug)
    synchronous.Backend().refresh(slug)


@shared_task
def django_datawatch_run(slug, identifier, *args, **kwargs):
    logger.debug('running check %s for identifier %s', slug, identifier)
    synchronous.Backend().run(slug, identifier)


class DatawatchScheduler(PeriodicTask):
    run_every = crontab(minute='*/1')
    queue = getattr(settings, 'DJANGO_DATAWATCH_CELERY_QUEUE_NAME',
                    defaults['CELERY_QUEUE_NAME'])

    def run(self, *args, **kwargs):
        Scheduler().run_checks(force=False)
