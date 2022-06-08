from healthcheck.settings.base import *  # noqa: F403

SECRET_KEY = "testsecretkey"
DEBUG = True
DATABASES = {
    "default": env.db(  # noqa: F405
        default="postgis://postgres:postgres@localhost:5432/healthcheck"
    ),
}

CELERY_ALWAYS_EAGER = True
CELERY_TASK_ALWAYS_EAGER = True

PROMETHEUS_EXPORT_MIGRATIONS = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default="*")  # noqa: F405
