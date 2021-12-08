import os

import environ

env = environ.Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
root = environ.Path(__file__) - 3
BASE_DIR = root()

SECRET_KEY = "replaceme"
DEBUG = True

DATABASES = {"default": env.db(default="sqlite:///")}

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # external packages
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "rest_auth",
    "phonenumber_field",
    "celery",
    "django_filters",
    "import_export",
    "drf_spectacular",
    # monitoring apps
    "django_prometheus",
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.contrib.redis",
    "health_check.contrib.rabbitmq",
    "health_check.contrib.celery_ping",
    # local apps
    "users",
    "contacts",
    "userprofile",
    "tbconnect",
    "selfswab",
    "lifenet",
    "vaccine",
    "vaxchamps",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "healthcheck.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "healthcheck.wsgi.application"


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Johannesburg"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django.contrib.staticfiles.finders.FileSystemFinder",
)

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

TIMEFRAME = env.int("TIMEFRAME", 14)

# Other config variables
AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "PAGE_SIZE": 1000,
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.CursorPagination",
}

SPECTACULAR_SETTINGS = {"TITLE": "HealthCheck"}

# this might be unneccessary if intented usage is international phone numbers
PHONENUMBER_DB_FORMAT = "NATIONAL"
PHONENUMBER_DEFAULT_REGION = "ZA"

# CELERY SETTINGS
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", "redis://localhost:6379/0")
# BROKER_URL and REDIS_URL are required to have rabbitmq and redis monitoring.
# Redis is used in dev env, RabbitMQ on production.
BROKER_URL = env.str("CELERY_BROKER_URL", "redis://localhost:6379/0")
REDIS_URL = env.str("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = env.str("CELERY_TASK_SERIALIZER", "json")
CELERY_RESULT_SERIALIZER = env.str("CELERY_RESULT_SERIALIZER", "json")

TURN_API_KEY = env.str("TURN_API_KEY", "default")
API_DOMAIN = env.str("API_DOMAIN", "https://whatsapp.turn.io/")
SENTRY_DSN = env.str("SENTRY_DSN", "")

RAPIDPRO_URL = env.str("RAPIDPRO_URL", "")
RAPIDPRO_TOKEN = env.str("RAPIDPRO_TOKEN", "")
RAPIDPRO_TBCONNECT_FLOW = env.str("RAPIDPRO_TBCONNECT_FLOW", "")

MEDITECH_URL = env.str("MEDITECH_URL", "")
MEDITECH_USER = env.str("MEDITECH_USER", "")
MEDITECH_PASSWORD = env.str("MEDITECH_PASSWORD", "")

SELFSWAB_RAPIDPRO_TOKEN = env.str("SELFSWAB_RAPIDPRO_TOKEN", "")
SELFSWAB_RAPIDPRO_FLOW = env.str("SELFSWAB_RAPIDPRO_FLOW", "")

VAXCHAMPS_RAPIDPRO_FLOW = env.str("VAXCHAMPS_RAPIDPRO_FLOW", "")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

TBCONNECT_BQ_KEY_PATH = env.str("TBCONNECT_BQ_KEY_PATH", "bq_credentials.json")
TBCONNECT_BQ_DATASET = env.str("TBCONNECT_BQ_DATASET", "wassup-165700.tbconnect")

SELFSWAB_BQ_KEY_PATH = env.str("SELFSWAB_BQ_KEY_PATH", "bq_credentials.json")
SELFSWAB_BQ_DATASET = env.str("SELFSWAB_BQ_DATASET", "wassup-165700.selfswab")

SELFSWAB_RETRY_HOURS = env.int("SELFSWAB_RETRY_HOURS", 8)

SELFSWAB_TURN_URL = env.str("SELFSWAB_TURN_URL", "https://whatsapp.turn.io/")
SELFSWAB_TURN_TOKEN = env.str("SELFSWAB_TURN_TOKEN", "default")

LIFENET_BQ_KEY_PATH = env.str("LIFENET_BQ_KEY_PATH", "bq_credentials.json")
LIFENET_BQ_DATASET = env.str("LIFENET_BQ_DATASET", "wassup-165700.lifenet")

CONTACT_NOTIFICATION_ENABLED = env.bool("CONTACT_NOTIFICATION_ENABLED", False)
