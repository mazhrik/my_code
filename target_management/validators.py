from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime


def validate_expiry_date(value):
    if value < timezone.now() + datetime.timedelta(hours=1):
        raise ValidationError("Expiry Date Should be not less than today")
    else:
        return value
