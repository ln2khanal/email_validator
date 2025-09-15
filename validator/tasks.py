from .models import Email
from celery import shared_task
from .constants import ValidationStaeChoices
from email_validator_api.logger import logger
from .views import get_email_validated_details

@shared_task
def validate_pending_emails_task(batch_size=100): # the batch size can be tuned as required.
    pending_emails = (
        Email.objects
        .filter(status=ValidationStaeChoices.pending)
        .order_by("created_at")[:batch_size]
    )
    for email in pending_emails:
        validate_email.delay(email.id, email.email)
    

@shared_task
def validate_email(email_id, email_address):
    validated_details = get_email_validated_details(email=email_address)
    logger.info(f"validating email complete; email={email_address}, details={validated_details}")
    Email.objects.filter(id=email_id).update(
        validation_details=validated_details,
        status=ValidationStaeChoices.checked,
    )
