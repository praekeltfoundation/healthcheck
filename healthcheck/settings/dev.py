from healthcheck.settings.base import *  # noqa: F403
import dj_database_url

SECRET_KEY = env.str("SECRET_KEY", "testsecretkey")  # noqa: F405
DEBUG = env.bool("DEBUG", True)  # noqa: F405
DATABASES = {
    "default": dj_database_url.config(
        "postgres://postgres:postgres@localhost:5432/healthcheck")
}
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default="*")  # noqa: F405
