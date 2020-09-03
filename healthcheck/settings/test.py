from healthcheck.settings.base import *  # noqa: F403

SECRET_KEY = "testsecretkey"
DEBUG = True
DATABASES = {
    "default": env.db(  # noqa: F405
        default="postgres://postgres:postgres@localhost:5432/healthcheck"
    ),
}

CELERY_ALWAYS_EAGER = True
CELERY_TASK_ALWAYS_EAGER = True
