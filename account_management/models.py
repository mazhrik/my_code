from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from django.utils.functional import cached_property

from account_management.constants import Notification_Status
from target_management.validators import validate_expiry_date
from django_currentuser.middleware import get_current_authenticated_user


def current_user(self):
    user = get_current_authenticated_user()
    return user


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.TextField(default='')
    last_name = models.TextField(default='')
    address = models.TextField(default='')
    employee_id = models.TextField(default='', unique=True)
    description = models.TextField(default='')
    date_of_birth = models.DateField(null=True, blank=True)
    # cnic = models.BigIntegerField()
    contact = models.BigIntegerField(null=True, blank=True)
    is_enabled = models.BooleanField(default=False)
    # login_count = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    expire_on = models.DateTimeField(
        default=timezone.now() + datetime.timedelta(hours=1),
        validators=[validate_expiry_date])
    updated_on = models.DateTimeField(auto_now=True)
    class Meta:

        permissions = [
            ("full_access_to_ums", "full access to ums"),
            ]    



    @cached_property
    def is_expired(self):
        return timezone.now() < self.expire_on

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_expired = models.BooleanField(default=False)
    date = models.DateTimeField(null=True, blank=True)
    block_count = models.PositiveIntegerField(default=0)


class AccountSettings(models.Model):
    """
    Model to create setting for user specific notifications response
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    OCS = models.CharField(choices=Notification_Status, default=Notification_Status[2], max_length=30)


class Team(models.Model):
    team_name = models.CharField(unique= True,max_length=255)
    description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    team_leader = models.OneToOneField(User, related_name='team_leader', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.team_leader.username# + " team leader of " +self.team_name  

class Team_members(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username 