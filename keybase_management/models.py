from django.db.models import Q

from account_management.models import current_user
from django.db import models
import datetime
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from target_management.validators import validate_expiry_date
from django.contrib.auth.models import User
from OCS_Rest.limitations import LIMITATIONS

# Create your models here.


class Keybase(models.Model):
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)
    title = models.TextField(default='', unique=True)
    description = models.TextField(default='', null=True)
    keywords = ArrayField(models.TextField(default=''), null=True)
    mentions = ArrayField(models.TextField(default=''), null=True)
    phrases = ArrayField(models.TextField(default=''), null=True)
    hashtags = ArrayField(models.TextField(default=''), null=True)
    is_enabled = models.BooleanField(editable=False)
    is_expired = models.BooleanField(editable=False)
    created_on = models.DateTimeField(editable=False)
    expire_on = models.DateTimeField(validators=[validate_expiry_date])
    updated_on = models.DateTimeField(editable=False)
    class Meta:

            ordering = ('-created_on',)
            permissions = [
            ("can_generatee_report", "Can generate marked report "),
            # ("can_create_keybase", "can create keybase"),
        ]


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.user = User.objects.get(username=current_user(self))
        self.created_on = timezone.now() + datetime.timedelta(hours=11)
        self.updated_on = timezone.now() + datetime.timedelta(hours=11)
        self.is_enabled = True
        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        super(Keybase, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        self.updated_on = timezone.now() + datetime.timedelta(hours=11)
        super(Keybase, self).save(*args, **kwargs)

    @staticmethod
    def get_keybase_count():
        keybase_count = Keybase.objects.filter(Q(created_on__icontains=datetime.datetime.date(datetime.datetime.now())))
        if keybase_count.count() < LIMITATIONS['Keybase']:
            return True
        else:
            return False
