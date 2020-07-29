from healthcheck.settings.base import *  # noqa: F403

SECRET_KEY = env.str("SECRET_KEY", "replaceme")  # noqa: F405
DEBUG = env.bool("DEBUG", False)  # noqa: F405
DATABASES = {
    "default": env.db(),  # noqa: F405
}
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # noqa: F405
