from healthcheck.settings.base import *  # flake8: noqa

SECRET_KEY = "testsecretkey"
DEBUG = True
DATABASES = {
    'default': env.db(default="sqlite:///"),
}

