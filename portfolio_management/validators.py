from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime


def validate_expiry_date(value):
    if value < timezone.now() + datetime.timedelta(hours=1):
        raise ValidationError("Expiry Date Should be not less than today")
    else:
        return value


def validate_event_date(value):
    if value > timezone.now() + datetime.timedelta(hours=1):
        raise ValidationError("Event date should be before then today's data")
    else:
        return value


def validate_dob(value):
    if value > datetime.date.today():
        raise ValidationError("DOB should be before then today's date")
    else:
        return value
