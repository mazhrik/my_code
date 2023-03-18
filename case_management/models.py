from django.db import models
import datetime
from django.db.models import JSONField
from django.db.models import Q
from django.utils import timezone
from gm2m import GM2MField as gm2m_field
from django.contrib.auth.models import User
from target_management.validators import validate_expiry_date
from case_management.validators import validate_incident_date
from case_management.constants import (SPOKEN_LANGUAGE_FLUENCY,
                                       LANGUAGE,
                                       INVESTIGATOR_TYPE,
                                       MEDIA_TYPE,
                                       GENDER,
                                       CASE_TYPE,
                                       PERSON_TYPE,
                                       CASE_PRIORITY,
                                       CASE_STATE,
                                       APP_PREFIX, INVESTIGATOR_PREFIX)
from account_management.models import current_user
from OCS_Rest.limitations import LIMITATIONS

from django.contrib.postgres.fields import ArrayField

# Create your models here.


class GM2MField(gm2m_field):
    def get_limit_choices_to(self):
        pass


class Location(models.Model):
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)


class Event(models.Model):
    name = models.TextField(default='')
    category = models.TextField(default='')
    description = models.TextField(default='')
    task = models.TextField(default='')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()


class Shape(models.Model):
    """
    This class is related to CaseInvestigationMap.
    All location of shapes stores here.
    """
    shape_raw = JSONField(default=dict)


# Case Maps
class CaseInvestigationMap(models.Model):
    """
    This class is used to access the location
    of the target.
    """

    map_name = models.CharField(max_length=20, default="")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    shapes = JSONField(default=dict, null=True)

    @staticmethod
    def get_object_by_id(obj_id):
        """
        This function returns the CaseInvestigation objects by id

        @params (Required)
        """

        return CaseInvestigationMap.objects.get(id=obj_id)


class Investigator(models.Model):
    """
    Investigator Model for Case
    """
    # image = models.ImageField(default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False, null=True)
    first_name = models.TextField(default='')
    image_url = models.URLField(default='', null=True)
    last_name = models.TextField(default='')
    employee_id = models.TextField(default='', unique=True)
    phone = models.TextField(default='')
    cnic = models.TextField(default='')
    email = models.TextField(default='')
    investigator_type = models.CharField(choices=INVESTIGATOR_TYPE, max_length=225)

    def save(self, *args, **kwargs):
        self.user = User.objects.get(username=current_user(self))
        super(Investigator, self).save(*args, **kwargs)
        return True


class Media(models.Model):
    """
    Investigator Model for Case
    """
    media_url = models.URLField(default='', null=True)
    media_title = models.TextField(unique=True, max_length=100)


class Person(models.Model):
    """
    Person Model for Case
    """
    first_name = models.TextField(default='')
    last_name = models.TextField(default='')
    description = models.TextField(default='')
    gender = models.CharField(choices=GENDER, max_length=225)
    phone = models.TextField(default='')
    cnic = models.TextField(default='')
    category = models.CharField(choices=PERSON_TYPE, max_length=225)
    email = models.TextField(default='')
    picture = models.URLField(default='')
    language = models.CharField(choices=LANGUAGE, max_length=225, default='english')
    accent = models.TextField(default='')
    can_read = models.BooleanField(default=False)
    can_write = models.BooleanField(default=False)
    can_speak = models.BooleanField(default=False)
    fluency = models.CharField(choices=SPOKEN_LANGUAGE_FLUENCY, max_length=225, default='beginner')
    # portfolio = ArrayField(models.ForeignKey(Portfolio, on_delete=models.CASCADE))


class Evidence(models.Model):
    """
    Evidence Module for case
    """
    title = models.TextField(default='')
    description = models.TextField(default='')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)


class Case(models.Model):
    """
    Case Management Main Module for case creation
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False, null=True)
    case_title = models.CharField(max_length=255,
                                  unique=True,
                                  null=False, blank=False)
    case_number = models.TextField(default='', editable=False)
    case_id = models.PositiveIntegerField(default=1, editable=False)
    is_enabled = models.BooleanField(default=True, editable=False)
    is_expired = models.BooleanField(default=False, editable=False)
    created_on = models.DateTimeField(editable=False)
    expire_on = models.DateTimeField(validators=[validate_expiry_date])
    updated_on = models.DateTimeField(auto_now=True)
    incident_datetime = models.DateTimeField(validators=[validate_incident_date])
    case_type = models.CharField(choices=CASE_TYPE, max_length=225)
    case_description = models.TextField(default='')
    case_priority = models.CharField(choices=CASE_PRIORITY, max_length=225)
    case_state = models.CharField(choices=CASE_STATE, max_length=225)
    investigators = models.ManyToManyField(Investigator, related_name='investigator', blank=True)
    people = models.ManyToManyField(Person, related_name='people', blank=True)
    locations = models.ManyToManyField(Location, related_name='locations', blank=True)
    media = models.ManyToManyField(Media, related_name='media', blank=True)
    evidences = models.ManyToManyField(Evidence, related_name='evidences', blank=True)
    case_map = models.ManyToManyField(CaseInvestigationMap, related_name='case_maps', blank=True)
    case_event = models.ManyToManyField(Event, related_name='case_event', blank=True)
    linked_data = GM2MField(blank=True)
    tao_investigator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='tao_investigator')
    share_resource = ArrayField(models.PositiveIntegerField() ,default=[])

    class Meta:
        ordering = ('-created_on',)

    def case_id_gen(self):
        if Case.objects.all().exists():
            self.case_id = Case.objects.latest('id').case_id + 1
        else:
            self.case_id = 1
        self.case_number = APP_PREFIX + str(self.case_id)

    def save(self, *args, **kwargs):
        self.user = User.objects.get(username=current_user(self))
        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        self.created_on = timezone.now() + datetime.timedelta(hours=11)
        self.case_id_gen()
        super(Case, self).save(*args, **kwargs)
        return True

    def update(self, *args, **kwargs):
        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        super(Case, self).save(*args, **kwargs)
        return True

    @staticmethod
    def get_case_count():
        print(datetime.datetime.date(datetime.datetime.now()))
        case_count = Case.objects.filter(Q(created_on__icontains=datetime.datetime.date(datetime.datetime.now())))
        if case_count.count() < LIMITATIONS['Case']:
            return True
        else:
            return False

    def __str__(self):
        return self.case_title