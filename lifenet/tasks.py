from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.conf import settings
from django_redis import get_redis_connection

from healthcheck import utils
from lifenet.models import LNCheck
from userprofile.models import HealthCheckUserProfile


@periodic_task(run_every=crontab(minute="*/5"))
def perform_etl():
    r = get_redis_connection()
    if r.get("perform_etl_ln_connect"):
        return

    models = {
        "checks": {
            "model": LNCheck,
            "field": "timestamp",
            "fields": {
                "deduplication_id": "STRING",
                "msisdn": "STRING",
                "timestamp": "TIMESTAMP",
                "source": "STRING",
                "age": "STRING",
                "cough": "BOOLEAN",
                "fever": "BOOLEAN",
                "sore_throat": "BOOLEAN",
                "difficulty_breathing": "BOOLEAN",
                "muscle_pain": "BOOLEAN",
                "smell": "BOOLEAN",
                "exposure": "STRING",
                "risk": "STRING",
                "tracing": "BOOLEAN",
                "language": "STRING",
            },
        }
    }

    with r.lock("perform_etl_lifenet", 1800):
        utils.sync_models_to_bigquery(
            settings.LIFENET_BQ_KEY_PATH, settings.LIFENET_BQ_DATASET, models
        )
