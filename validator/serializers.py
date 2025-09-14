from rest_framework import serializers

class EmailListSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.EmailField())