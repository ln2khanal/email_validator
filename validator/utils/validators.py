import os
import socket
import smtplib
import dns.resolver
from email_validator import validate_email, EmailNotValidError
import asyncio
import aiosmtplib
from .cache import cached

from email_validator_api.logger import logger

resolver = dns.resolver.Resolver()

resolver.lifetime = 5.0
from_email_address = os.getenv("FROM_EMAIL_ADDRESS", "info@org.local")

@cached() # we can speedup for any duplications
def check_format(email):
    try:
        logger.debug(f"validating emails {email}")
        v = validate_email(email)
        return True, v['email']
    except (EmailNotValidError, Exception) as e:
        logger.exception(f"email address couldn't be validated, email={email}, error={str(e)}")
    return False, None

@cached()
def get_mx_records(domain):
    try:
        logger.debug(f"validating domain {domain}")
        answers = resolver.resolve(domain, 'MX')
        mxs = sorted([(r.preference, str(r.exchange).rstrip('.')) for r in answers], key=lambda x: x[0])
        return [m[1] for m in mxs]
    except Exception as e:
        logger.exception(f"mx_records couldn't be read, domain={domain}, error={str(e)}")
        return []

@cached()
def check_spf(domain):
    try:
        answers = resolver.resolve(domain, 'TXT')
        txts = [b''.join(r.strings).decode('utf-8', errors='ignore') for r in answers]
        spf = [t for t in txts if 'v=spf1' in t.lower()]
        logger.debug(f"emails spf check answers={answers} spf={spf}, domain={domain}")
        return spf[0] if spf else None
    except Exception as e:
        logger.error(f"couldn't check spf domain={domain}, error={str(e)}")
        return None

@cached()
def check_dmarc(domain):
    try:
        d = f'_dmarc.{domain}'
        answers = resolver.resolve(d, 'TXT')
        txts = [b''.join(r.strings).decode('utf-8', errors='ignore') for r in answers]
        logger.debug(f"dmarc check for domain={domain}, answers={answers}, txts={txts}")
        return txts[0] if txts else None
    except Exception as e:
        logger.exception(f"couldn't check dmarc domain={domain}")
        return None

@cached()
def check_dkim(domain, selector='default'):
    try:
        name = f'{selector}._domainkey.{domain}'
        answers = resolver.resolve(name, 'TXT')
        txts = [b''.join(r.strings).decode('utf-8', errors='ignore') for r in answers]
        logger.debug(f"dkim check for domain={domain}, name={name}, answers={answers}")
        if txts:
            return selector, txts[0]
    except dns.resolver.NXDOMAIN:
        logger.info(f"DKIM selector not found: {selector} for domain={domain}")
    except Exception as e:
        logger.exception(f"checking dkim for domain={domain}, selector={selector}, error={str(e)}")
    return None

async def _smtp_check_single_host(host, from_address, target_email, timeout):
    try:
        server = aiosmtplib.SMTP(hostname=host, port=25, timeout=timeout)
        await server.connect()
        await server.ehlo()
        await server.mail(from_address)
        code, resp = await server.rcpt(target_email)
        await server.quit()
        logger.debug(f"checking smtp; server={server}, code={code}, resp={resp}")
        if code and 200 <= code < 300 or code == 250 or code == 251:
            return True, f'{code} {resp}'
        else:
            return False, f'{code} {resp}'
    except (aiosmtplib.errors.SMTPRecipientsRefused, aiosmtplib.errors.SMTPException, socket.error) as e:
        last_err = str(e)
        logger.error(f"couldn't check smtp for host={host}, from_address={from_address}, target_email={target_email} error={str(e)}")
        return False, last_err

@cached()
async def smtp_check(mx_hosts, from_address='validator@example.com', target_email=None, timeout=5):
    if not mx_hosts:
        return False, 'no-mx'
    tasks = [
        asyncio.create_task(_smtp_check_single_host(host, from_address, target_email, timeout))
        for host in mx_hosts
    ]
    done, pending = await asyncio.wait(tasks, timeout=timeout, return_when=asyncio.FIRST_COMPLETED)
    for task in done:
        result, info = task.result()
        if result:
            for p in pending:
                p.cancel()
            return True, info

    errors = [task.result()[1] for task in done]
    for p in pending:
        p.cancel()
    return False, errors[0] if errors else 'unknown-error'