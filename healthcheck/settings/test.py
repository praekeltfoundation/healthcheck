from healthcheck.settings.base import *  # noqa: F403

SECRET_KEY = "testsecretkey"
DEBUG = True
DATABASES = {
    "default": env.db(default="sqlite:///"),  # noqa: F405
}

CELERY_ALWAYS_EAGER = True
CELERY_TASK_ALWAYS_EAGER = True
