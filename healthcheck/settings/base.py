from celery.schedules import crontab
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
    "django.contrib.gis",
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
    "django_celery_results",
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
    "covid_cases",
    "userprofile",
    "tbconnect",
    "selfswab",
    "lifenet",
    "real411",
    "vaccine",
    "vaxchamps",
    "clinicfinder",
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
        "rest_framework.authentication.SessionAuthentication",
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
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = env.str("CELERY_TASK_SERIALIZER", "json")
CELERY_RESULT_SERIALIZER = env.str("CELERY_RESULT_SERIALIZER", "json")
CELERY_BEAT_SCHEDULE = {
    "scrape-nicd-gis": {
        "task": "covid_cases.tasks.scrape_nicd_gis",
        "schedule": crontab(minute="0"),
    },
    "scrape-sacoronavirus": {
        "task": "covid_cases.tasks.scrape_sacoronavirus_homepage",
        "schedule": crontab(minute="0"),
    },
    "scrape-sacoronavirus-images": {
        "task": "covid_cases.tasks.scrape_sacoronavirus_case_images",
        "schedule": crontab(minute="0"),
    },
    "perform-notifications-check": {
        "task": "contacts.tasks.perform_notifications_check",
        "schedule": crontab(minute=50, hour=1),
    },
    "perform-sync-to-rapidpro": {
        "task": "tbconnect.tasks.perform_sync_to_rapidpro",
        "schedule": crontab(minute="*/1"),
    },
    "perform-tbconnect-etl": {
        "task": "tbconnect.tasks.perform_etl",
        "schedule": crontab(minute="*/5"),
    },
    "perform-lifenet-etl": {
        "task": "lifenet.tasks.perform_etl",
        "schedule": crontab(minute="*/5"),
    },
}

TURN_API_KEY = env.str("TURN_API_KEY", "default")
API_DOMAIN = env.str("API_DOMAIN", "https://whatsapp.turn.io/")
SENTRY_DSN = env.str("SENTRY_DSN", "")

RAPIDPRO_URL = env.str("RAPIDPRO_URL", "")
RAPIDPRO_TOKEN = env.str("RAPIDPRO_TOKEN", "")
RAPIDPRO_TBCONNECT_FLOW = env.str("RAPIDPRO_TBCONNECT_FLOW", "")
RAPIDPRO_REAL411_FLOW = env.str("RAPIDPRO_REAL411_FLOW", "")

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
        "KEY_PREFIX": env.str("REDIS_PREFIX", ""),
    }
}

TBCONNECT_BQ_KEY_PATH = env.str("TBCONNECT_BQ_KEY_PATH", "bq_credentials.json")
TBCONNECT_BQ_DATASET = env.str("TBCONNECT_BQ_DATASET", "wassup-165700.tbconnect")

TB_STUDY_A_MAX_COUNT = env.int("TB_STUDY_A_MAX_COUNT", 1125)
TB_STUDY_B_MAX_COUNT = env.int("TB_STUDY_B_MAX_COUNT", 1125)
TB_STUDY_C_MAX_COUNT = env.int("TB_STUDY_C_MAX_COUNT", 15000)

TB_STUDY_A_END_DATE = env.str("TB_STUDY_A_END_DATE", "2023-11-16")
TB_STUDY_B_END_DATE = env.str("TB_STUDY_B_END_DATE", "2023-11-16")
TB_STUDY_C_END_DATE = env.str("TB_STUDY_C_END_DATE", "2023-12-16")

SELFSWAB_BQ_KEY_PATH = env.str("SELFSWAB_BQ_KEY_PATH", "bq_credentials.json")
SELFSWAB_BQ_DATASET = env.str("SELFSWAB_BQ_DATASET", "wassup-165700.selfswab")

SELFSWAB_RETRY_HOURS = env.int("SELFSWAB_RETRY_HOURS", 8)

SELFSWAB_TURN_URL = env.str("SELFSWAB_TURN_URL", "https://whatsapp.turn.io/")
SELFSWAB_TURN_TOKEN = env.str("SELFSWAB_TURN_TOKEN", "default")

LIFENET_BQ_KEY_PATH = env.str("LIFENET_BQ_KEY_PATH", "bq_credentials.json")
LIFENET_BQ_DATASET = env.str("LIFENET_BQ_DATASET", "wassup-165700.lifenet")

CONTACT_NOTIFICATION_ENABLED = env.bool("CONTACT_NOTIFICATION_ENABLED", False)

ENABLE_NICD_GIS_SCRAPING = env.bool("ENABLE_NICD_GIS_SCRAPING", False)
ENABLE_SACORONAVIRUS_SCRAPING = env.bool("ENABLE_SACORONAVIRUS_SCRAPING", False)

DEFAULT_FILE_STORAGE = env.str(
    "DEFAULT_FILE_STORAGE", "django.core.files.storage.FileSystemStorage"
)
AWS_S3_ACCESS_KEY_ID = env.str("AWS_S3_ACCESS_KEY_ID", "")
AWS_S3_SECRET_ACCESS_KEY = env.str("AWS_S3_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", "")
AWS_S3_OBJECT_PARAMETERS = env.dict("AWS_S3_OBJECT_PARAMETERS", default={})
AWS_DEFAULT_ACL = env.str("AWS_DEFAULT_ACL", None)
AWS_LOCATION = env.str("AWS_LOCATION", "")
AWS_S3_REGION_NAME = env.str("AWS_S3_REGION_NAME", None)
AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", None)

LOCATION_SEARCH_RADIUS = env.int("LOCATION_SEARCH_RADIUS", 20)

ALLOW_TB_RESET_MSISDNS = env.list("ALLOW_TB_RESET_MSISDNS", default=[])

SOFT_COMMITMENT_PLUS_LIMIT = env.int("SOFT_COMMITMENT_PLUS_LIMIT", 3000)

CCI_URL = env.str("CCI_URL", None)
