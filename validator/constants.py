from django.db import models

class ValidationStaeChoices(models.TextChoices):
    pending = "pending", "PENDING"
    checked = "checked", "checked"
