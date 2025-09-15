
from .models import Email
from rest_framework import status
from rest_framework.response import Response
from .constants import ValidationStaeChoices
from rest_framework.viewsets import ModelViewSet
from .serializers import ListCheckedEmailSerializer, BulkEmailInputSerializer

class ValidateEmailsCheckedListAPI(ModelViewSet):
    queryset = Email.objects.all()
    serializer_class = ListCheckedEmailSerializer
    
    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.queryset)
        serializer = self.get_serializer(page, many=True)

        total = Email.objects.count()
        checked = Email.objects.filter(status=ValidationStaeChoices.checked).count()
        pending = Email.objects.filter(status=ValidationStaeChoices.pending).count()

        paginated_response = self.get_paginated_response(serializer.data)
        paginated_response.data.update({
            "total": total,
            "checked": checked,
            "pending": pending,
        })
        
        return paginated_response

    def create(self, request, *args, **kwargs):
        input_serializer = BulkEmailInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        emails = input_serializer.validated_data["emails"]

        created = Email.objects.bulk_create(
            [Email(email=e) for e in emails],
            ignore_conflicts=True
        )
        return Response(
            {"created_count": len(created), "input_count": len(emails)},
            status=status.HTTP_201_CREATED
        )