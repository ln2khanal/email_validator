from rest_framework import serializers
from .models import Email
class EmailListSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.EmailField())
    
class ListCheckedEmailSerializer(serializers.ModelSerializer):
    valid_format = serializers.SerializerMethodField()
    dns_mx = serializers.SerializerMethodField()
    spf = serializers.SerializerMethodField()
    dkim = serializers.SerializerMethodField()
    dmarc = serializers.SerializerMethodField()
    smtp_reachable = serializers.SerializerMethodField()
    smtp_info = serializers.SerializerMethodField()
    class Meta:
        model = Email
        fields = [
            "id",
            "email",
            "valid_format",
            "dns_mx",
            "spf",
            "dkim",
            "dmarc",
            "smtp_reachable",
            "smtp_info",
            "status",
        ]
        
    def get_valid_format(self, obj):
        return obj.validation_details.get("valid_format") if obj.validation_details else None

    def get_dns_mx(self, obj):
        return obj.validation_details.get("dns_mx") if obj.validation_details else None

    def get_spf(self, obj):
        return obj.validation_details.get("spf") if obj.validation_details else None

    def get_dkim(self, obj):
        return obj.validation_details.get("dkim") if obj.validation_details else None

    def get_dmarc(self, obj):
        return obj.validation_details.get("dmarc") if obj.validation_details else None

    def get_smtp_reachable(self, obj):
        return obj.validation_details.get("smtp_reachable") if obj.validation_details else None

    def get_smtp_info(self, obj):
        return obj.validation_details.get("smtp_info") if obj.validation_details else None
class BulkEmailInputSerializer(serializers.Serializer):
    emails = serializers.ListField(
        child=serializers.EmailField(),
        allow_empty=False,
        help_text="List of email addresses"
    )