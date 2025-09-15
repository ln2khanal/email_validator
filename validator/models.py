from django.db import models
from .constants import ValidationStaeChoices

class Email(models.Model):
    email = models.EmailField(unique=True)
    status = models.CharField(
        choices=ValidationStaeChoices.choices,
        blank=False,
        default=ValidationStaeChoices.pending
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    validation_details = models.JSONField(null=True, blank=True, default=dict)