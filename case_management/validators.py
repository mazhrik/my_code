from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_incident_date(value):
    if value > timezone.now():
        raise ValidationError("Incident Date Should be less than today")
    else:
        return value
