from healthcheck.settings.base import *  # noqa: F403

SECRET_KEY = "testsecretkey"
DEBUG = True
DATABASES = {
    "default": env.db(default="sqlite:///"),  # noqa: F405
}
