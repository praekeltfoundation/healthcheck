from healthcheck.settings.base import *  # flake8: noqa


SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG", False)
DATABASES = {
    'default': env.db(),
}
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
