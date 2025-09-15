from .models import Email
from celery import shared_task
from email_validator_api.logger import logger

@shared_task
def validate_pending_emails_task():
    pending_emails = Email.objects.filter(status="pending")
    for email in pending_emails:
        do_nothing.delay(email.email)


@shared_task
def do_nothing(email=None):
    logger.info(f"Do nothing is being called. Email={email}")
    pass
