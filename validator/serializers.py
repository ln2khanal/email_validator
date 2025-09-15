from rest_framework import serializers
from .models import Email
class EmailListSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.EmailField())
    
class ListCheckedEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = "__all__"
        
class BulkEmailInputSerializer(serializers.Serializer):
    emails = serializers.ListField(
        child=serializers.EmailField(),
        allow_empty=False,
        help_text="List of email addresses"
    )