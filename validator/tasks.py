from asgiref.sync import async_to_sync
from .utils import validators as validator_core
from email_validator_api.logger import logger

from .models import Email
from celery import shared_task
from .constants import ValidationStaeChoices
from email_validator_api.logger import logger

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


def get_email_validated_details(email:str):
    """validates different properties of an email address by initiating http calls

    Args:
        email (str): email field to validate

    Returns:
        _type_: dict object
    """
    result = {
        'email': email, 
        'dns_mx': False,
        'smtp_reachable': False,
        'spf': None,
        'dkim': None,
        'dmarc': None,
        'status': "unknown"
    }
    ok_fmt, normalized = validator_core.check_format(email)
    result['valid_format'] = ok_fmt
    
    if ok_fmt:
        domain = normalized.split('@',1)[1]
        mx = validator_core.get_mx_records(domain)
        result['dns_mx'] = bool(mx)
        
        logger.info("validating SPF")
        result['spf'] = validator_core.check_spf(domain)
        
        logger.info("validating DKIM")
        dkim = validator_core.check_dkim(domain)
        result['dkim'] = {'selector': dkim[0], 'record': dkim[1]} if dkim else None
        
        logger.info("validating DMARC")
        result['dmarc'] = validator_core.check_dmarc(domain)
        
        logger.info("validating SMTP")
        smtp_ok, smtp_info = async_to_sync(validator_core.smtp_check)(mx, target_email=normalized)
        result['smtp_reachable'] = smtp_ok
        result['smtp_info'] = smtp_info
        
        if smtp_ok:
            result['status'] = 'deliverable'
        elif result['dns_mx'] and not smtp_ok:
            result['status'] = 'unknown' 
        else:
            result['status'] = 'undeliverable'
    return result