from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import async_to_sync
from .serializers import EmailListSerializer
from .utils import validators as validator_core
from email_validator_local.logger import logger

class ValidateEmailsView(APIView):
    def post(self, request):
        serializer = EmailListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        emails = serializer.validated_data['emails']
        results = []
        for email in emails:
            result = {'email': email}
            ok_fmt, normalized = validator_core.check_format(email)
            result['valid_format'] = ok_fmt
            if not ok_fmt:
                result.update({
                    'dns_mx': False,
                    'smtp_reachable': False,
                    'spf': None,
                    'dkim': None,
                    'dmarc': None,
                    'status': 'invalid_format'
                })
                results.append(result)
                continue
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
            results.append(result)
        return Response(results, status=status.HTTP_200_OK)
