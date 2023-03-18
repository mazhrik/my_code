from django.contrib.postgres.fields import ArrayField
from django.db import models
import datetime
from django.utils import timezone
from keybase_management.models import Keybase
from account_management.models import User
from target_management.constants import (
    PERIODIC_INTERVALS,
    TARGET_TYPE,
    TARGET_SUB_TYPE,
    TARGET_INDEX_RESOLVE,
    DOCUMENTS_TYPE_CHOICES)
from .validators import validate_expiry_date
from account_management.models import current_user
from core_management.elasticsearch_handler import ElasticsearchHandler
from django.db.models import Q
from OCS_Rest.limitations import LIMITATIONS
# Create your models here.

elasticsearch_obj = ElasticsearchHandler()


class GTR(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    @staticmethod
    def get_gtr(model_type, target_type):
        return str('{0}_{1}_{2}'.format(model_type,
                                        target_type,
                                        GTR.objects.create()))


class Target(models.Model):
    target_url = models.URLField(default='', max_length=5000)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, editable=False, null=True)
    GTR = models.TextField(default='st_st_1', editable=False)
    is_enabled = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False, editable=False)
    target_status = models.PositiveIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True,editable=False)
    expire_on = models.DateTimeField(validators=[validate_expiry_date])
    updated_on = models.DateTimeField(auto_now=True)
    periodic_interval = models.IntegerField(default=0,
                                            choices=PERIODIC_INTERVALS)
    target_status_string = models.TextField(default='Successful! target added', editable=False)
    target_status_dic = models.JSONField(default={"1": {"time": "", "message": "Target Marked"}})
    need_screenshot = models.BooleanField(default=False)
    revoked_on = models.DateTimeField(editable=False, null=True, default=timezone.now())
    operations = models.JSONField(default=dict)
    share_resource = ArrayField(models.PositiveIntegerField() ,default=[])


    class Meta:
        abstract = True
        ordering = ('-created_on',)
        permissions = [
            ("can_view_details", "Can view details"),
            ("can_mark_targets","can mark target"),
            # ("can_identify","can identify target"),
            # ("can_smartsearch","can smart search"),
            # ("can_create_bulk_target","can create bulk target"),
            ("can_create_internet_survey","can create internet survey"),
            ("can_perform_operations","can perform operations"),
            ]    

    @staticmethod
    def get_response_by_object(target_object):
        return target_object.GTR

    @staticmethod
    def get_all_responses(choice, gtr_id):
        if choice in TARGET_INDEX_RESOLVE:
            index = choice
        target_response = elasticsearch_obj.get_target_response(index)
        return target_response

    @staticmethod
    def get_response_by_type_and_id(index_choice, type_choice, id):
        if index_choice in TARGET_INDEX_RESOLVE:
            index = index_choice
        if type_choice in DOCUMENTS_TYPE_CHOICES:
            document_type = type_choice
        target_response = elasticsearch_obj.get_response_by_id_and_type(index, document_type, id)
        return target_response

    @staticmethod
    def get_response_by_type_gtr(choice, id, gtr_id):
        if choice in TARGET_INDEX_RESOLVE:
            index = choice

        # gtr_id = self.GTR
        document_type = ""
        target_response = elasticsearch_obj.get_response_by_id_and_type(index, document_type, gtr_id)
        return target_response

    @staticmethod
    def update_status(obj, updated_status, string_status):
        try:
            obj.target_status = updated_status
            obj.target_status_string = string_status
            updated = obj.update()
            return updated
        except Exception as E:
            print(E)
            return False

    @staticmethod
    def update_ctr(obj, ctr, new_revoke):
        try:
            obj.revoked_on = new_revoke
            obj.CTR = ctr + 1
            updated = obj.update()
            return updated
        except Exception as E:
            print(E)
            return False

    @staticmethod
    def get_response():
        pass

    @staticmethod
    def get_posts():
        pass

    @staticmethod
    def get_target_info():
        pass

    @staticmethod
    def get_profile_info():
        pass

    @staticmethod
    def close_associates():
        pass


class SocialTarget(Target):
    userid = models.TextField(default='')
    user_names = models.TextField(default='')
    full_name = models.TextField(default='')
    target_type = models.CharField(choices=TARGET_TYPE, max_length=225)
    CTR = models.PositiveIntegerField(default=1, editable=False)
    target_sub_type = models.CharField(choices=TARGET_SUB_TYPE, max_length=225)
    max_posts = models.PositiveIntegerField(default=0)
    avatar_username = models.CharField(default='', max_length=225)
    avatar_password = models.CharField(default='', max_length=225)

    class Meta:
        unique_together = (('user_names', 'target_type'),)

    def save(self, *args, **kwargs):
        self.user = User.objects.get(username=current_user(self))
        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        self.created_on = timezone.now() + datetime.timedelta(hours=11)
        self.GTR = GTR.get_gtr('st', self.target_type)
        self.operations = {'emotions_analyst': False, 'sentiment_analysis': False, 'text_categorization': False,
                           'target_summary': False, 'word_cloud': False, 'posts_frequent_graph': False,
                           'frequent_hashtags': False, 'common_words': False}
        super(SocialTarget, self).save(*args, **kwargs)
        return True

    def update(self, *args, **kwargs):
        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        super(SocialTarget, self).save(*args, **kwargs)
        return True

    @staticmethod
    def get_social_target_count():
        print(datetime.datetime.date(datetime.datetime.now()))
        case_count = SocialTarget.objects.filter(Q(created_on__icontains=datetime.datetime.date(datetime.datetime.now())))
        if case_count.count() < LIMITATIONS['SocialTarget']:
            return True
        else:
            return False

class LeakedData(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, editable=False, null=True)
    CTR = models.PositiveIntegerField(default=1, editable=False)
    target_type=models.CharField(max_length=225)
    created_on = models.DateTimeField(auto_now_add=True,editable=False)
    GTR = models.TextField(default='st_st_1', editable=False)
    file_name = models.CharField(max_length=255, default='')
    file_size = models.CharField(max_length=255, default='')
    
    
    def save(self, *args, **kwargs):
        target_dict = {
                'facebook': 'fb',
                'twitter': 'tw',
                'instagram': 'in',
                'linkedin': 'ln',
                'tiktok': 'tk',
                'other': 'other',
            }
        self.user = User.objects.get(username=current_user(self))
        self.created_on = timezone.now() + datetime.timedelta(hours=11)
        targettype=target_dict[self.target_type]
        self.GTR = GTR.get_gtr('ld', targettype)
        super(LeakedData, self).save(*args, **kwargs)
        
        return True

    


class GenericTarget(Target):
    title = models.TextField(default='')
    url = models.URLField(default='', unique=True)
    ip = models.BooleanField(default=False)
    domain = models.BooleanField(default=False)
    pictures = models.BooleanField(default=False)
    CTR = models.PositiveIntegerField(default=1, editable=False)
    videos = models.BooleanField(default=False)
    target_type = models.CharField(choices=TARGET_TYPE, max_length=225)
    target_sub_type = models.CharField(choices=TARGET_SUB_TYPE, max_length=225)
    headings = models.BooleanField(default=False)
    paragraphs = models.BooleanField(default=False)
    links = models.BooleanField(default=False)
    vpn = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.user = User.objects.get(username=current_user(self))
        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        self.created_on = timezone.now() + datetime.timedelta(hours=11)
        self.GTR = GTR.get_gtr('dt', self.target_type)
        self.operations = {'emotions_analyst': False, 'sentiment_analysis': False, 'text_categorization': False,
                           'target_summary': False, 'word_cloud': False, 'posts_frequent_graph': False,
                           'frequent_hashtags': False, 'common_words': False}
        super(GenericTarget, self).save(*args, **kwargs)
        return True

    def update(self, *args, **kwargs):
        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        super(GenericTarget, self).save(*args, **kwargs)
        return True

    @staticmethod
    def get_generic_target_count():
        print(datetime.datetime.date(datetime.datetime.now()))
        case_count = GenericTarget.objects.filter(Q(created_on__icontains=datetime.datetime.date(datetime.datetime.now())))
        if case_count.count() < LIMITATIONS['GenericTarget']:
            return True
        else:
            return False


class KeybaseTarget(Target):
    keybase = models.ForeignKey(Keybase,
                                on_delete=models.CASCADE,
                                null=True)
    keybase_title = models.TextField(default='')
    CTR = models.PositiveIntegerField(default=1, editable=False)
    target_type = models.CharField(choices=TARGET_TYPE, max_length=225)
    target_sub_type = models.CharField(choices=TARGET_SUB_TYPE, max_length=225)
    site = models.TextField(default='')

    def save(self, *args, **kwargs):
        self.user = User.objects.get(username=current_user(self))
        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        self.created_on = timezone.now() + datetime.timedelta(hours=11)
        self.GTR = GTR.get_gtr('kb', self.target_type)
        self.operations = {'emotions_analyst': False, 'sentiment_analysis': False, 'text_categorization': False,
                           'target_summary': False, 'word_cloud': False, 'posts_frequent_graph': False,
                           'frequent_hashtags': False, 'common_words': False}
        super(KeybaseTarget, self).save(*args, **kwargs)
        return True

    def update(self, *args, **kwargs):
        try:
            self.is_expired = timezone.now() > self.expire_on
        except TypeError:
            self.is_expired = datetime.datetime.now() > self.expire_on
        super(KeybaseTarget, self).save(*args, **kwargs)
        return True

    @staticmethod
    def get_keybase_target_count():
        print(datetime.datetime.date(datetime.datetime.now()))
        case_count = KeybaseTarget.objects.filter(Q(created_on__icontains=datetime.datetime.date(datetime.datetime.now())))
        if case_count.count() < LIMITATIONS['GenericTarget']:
            return True
        else:
            return False

class UserNews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    news_name = models.CharField(max_length=200)
    channel_url = models.URLField(blank=True, null=True)
    class Meta:
        unique_together = (('user', 'news_name'),)

    def __str__(self):
        return self.user.username
