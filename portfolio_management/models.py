from django.db import models
from django.db.models import Q
from django.contrib.postgres.fields import ArrayField
from account_management.models import User
from django.utils import timezone
from keybase_management.models import Keybase
from .constants import GENDER
import datetime
from case_management.models import Case
from .validators import validate_event_date, validate_expiry_date, validate_dob
from account_management.models import current_user
from gm2m import GM2MField as gm2m_field
from OCS_Rest.limitations import LIMITATIONS


class GM2MField(gm2m_field):
    def get_limit_choices_to(self):
        pass

# Create your models here.


class LinkedData(models.Model):
    type = models.TextField(default='')
    query = models.TextField(default='')
    data = models.JSONField(default=dict, null=True)


class Portfolio(models.Model):
    class Meta:
        abstract = True

        permissions = [
            # ("can_create_event_portfolio", "Can create event porttfolio "),
            # ("can_create_group_portfolio", "Can create group portfolio "),
            # ("can_create_individual_portfolio", "Can create individual portfolio "),
            # ("can_update_event_portfolio", "can update event portfolio"),
            # ("can_access_individual_portfolio", "can access individual portfolio"),
            # ("can_access_linked_info", "can access linked info"),
            ] 


    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=225, default='', unique=True)
    created_on = models.DateTimeField(editable=False)
    updated_on = models.DateTimeField(auto_now=True)
    expire_on = models.DateTimeField(validators=[validate_expiry_date])
    keybase = models.ManyToManyField(Keybase, blank=True)
    case = models.ManyToManyField(Case, blank=True)
    target = GM2MField(blank=True)
    portfolio = GM2MField(blank=True)
    linked_data = models.ManyToManyField(LinkedData, blank=True)
    address = models.TextField(default='')
    phone_number = models.TextField(default='')
    description = models.TextField(default='', null=True)
    share_resource = ArrayField(models.PositiveIntegerField() ,default=[])


class Individual(Portfolio):
    date_of_birth = models.DateField(validators=[validate_dob], null=True)
    gender = models.CharField(choices=GENDER, max_length=225, null=True)
    religion = models.CharField(default='', max_length=225, null=True)
    sect = models.CharField(default='', max_length=225, null=True)

    def save(self, *args, **kwargs):
        self.user = User.objects.get(username=current_user(self))
        print(self.user)
        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        self.created_on = timezone.now() + datetime.timedelta(hours=11)
        self.updated_on = timezone.now() + datetime.timedelta(hours=11)
        super(Individual, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        self.updated_on = timezone.now() + datetime.timedelta(hours=11)
        super(Individual, self).save(*args, **kwargs)

    @staticmethod
    def get_individual_portfolio_count():
        individual_portfolio_count = Individual.objects.filter(Q(created_on__icontains=datetime.datetime.date
        (datetime.datetime.now())))

        if individual_portfolio_count.count() < LIMITATIONS['Individual_Portfolio']:
            return True
        else:
            return False


class Group(Portfolio):
    group_type = models.CharField(default='', max_length=225)
    region = models.CharField(default='', max_length=225)
    details = models.CharField(default='', max_length=500)

    def save(self, *args, **kwargs):
        self.user = User.objects.get(username=current_user(self))

        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        self.created_on = timezone.now() + datetime.timedelta(hours=11)
        self.updated_on = timezone.now() + datetime.timedelta(hours=11)
        super(Group, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        self.updated_on = timezone.now() + datetime.timedelta(hours=11)
        super(Group, self).save(*args, **kwargs)

    @staticmethod
    def get_group_portfolio_count():
        group_portfolio_count = Group.objects.filter(Q(created_on__icontains=datetime.datetime.
                                                       date(datetime.datetime.now())))

        if group_portfolio_count.count() < LIMITATIONS['Group_Portfolio']:
            return True
        else:
            return False


class Event(Portfolio):
    event_date = models.DateTimeField(validators=[validate_event_date])
    event_type = models.CharField(default='', max_length=225)
    location = models.CharField(default='', max_length=225)
    event_details = models.CharField(default='', max_length=500)

    def save(self, *args, **kwargs):
        self.user = User.objects.get(username=current_user(self))

        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        self.created_on = timezone.now() + datetime.timedelta(hours=11)
        self.updated_on = timezone.now() + datetime.timedelta(hours=11)
        super(Event, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        self.updated_on = timezone.now() + datetime.timedelta(hours=11)
        super(Event, self).save(*args, **kwargs)

    @staticmethod
    def get_events_portfolio_count():
        event_portfolio_count = Event.objects.filter(Q(created_on__icontains=datetime.datetime.date(
            datetime.datetime.now())))

        if event_portfolio_count.count() < LIMITATIONS['Event_Portfolio']:
            return True
        else:
            return False
