
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "email_validator_api.settings")

app = Celery("email_validator_api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
