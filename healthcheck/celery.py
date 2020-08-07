from __future__ import absolute_import

import os

import sentry_sdk
from celery import Celery
from django.conf import settings
from sentry_sdk.integrations.celery import CeleryIntegration

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthcheck.settings.base")

app = Celery(__name__)
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

# this will ensure turn.io rate limiter does not return 429
app.control.rate_limit("contacts.tasks.send_contact_update", "60/m")

# only connect to sentry if dsn is supplied
if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, integrations=[CeleryIntegration()])
