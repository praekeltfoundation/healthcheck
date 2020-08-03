from celery import Celery

app = Celery("healthcheck")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

# this will ensure turn.io rate limiter does not return 429
app.control.rate_limit("contacts.tasks.send_contact_update", "60/m")


# fix the celery.ping assertion error in testing
@app.task(name="celery.ping")
def ping():
    # type: () -> str
    """Simple task that just returns 'pong'."""
    return "pong"
