from django.db import models
from django.utils.translation import gettext as _
import datetime
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.


class AddAccount(models.Model):
    username = models.CharField(max_length=225, default='', null=False)
    password = models.CharField(max_length=225, default='')
    email = models.EmailField()
    social_media = models.CharField(max_length=225, default='')
    friends_list = models.JSONField(default="[]", null=True, blank=True)
    created_on = models.DateField(default=datetime.date.today())
    created_by = models.CharField(max_length=225, default='')
    status = models.BooleanField(default=True)
    friends_groups= models.JSONField(default="[]", null=True, blank=True)

    def __str__(self):
        return self.username
    


class AvatarProfile(models.Model):
    first_name = models.CharField(max_length=225, default='')
    last_name = models.CharField(max_length=225, default='')
    email = models.EmailField(default='')
    phone_number = models.TextField(default=0)
    nationality = models.CharField(max_length=225, default='')
    address = models.CharField(max_length=225, default='')
    religion = models.CharField(max_length=225, default='')
    martial_status = models.CharField(max_length=225, default='')
    date_of_birth = models.DateField(default=datetime.date.today())
    
    class Meta:
        verbose_name = ("Log")
        verbose_name_plural = ("Logs")
        permissions = [
            ("amu_permission","all_amu_permission"),
            ]    





class AvatarCommentAction(models.Model):
    comment_text = models.TextField(default='')
    target_post_url = models.URLField(default='')
    comment_date = models.DateTimeField(editable=True)
    account = models.ForeignKey(AddAccount, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

class AvatarPostAction(models.Model):
    post_text = models.TextField(default='')
    post_date = models.DateTimeField(editable=True)
    account = models.ForeignKey(AddAccount, on_delete=models.CASCADE)
    image_url = models.URLField(default='', max_length=5000)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
class AvatarReactionAction(models.Model):
    reaction_type = models.CharField(max_length=225, default='')
    target_post_url = models.URLField(default='')
    reaction_date = models.DateTimeField(editable=True)
    account = models.ForeignKey(AddAccount, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
class AvatarMessageAction(models.Model):
    title = models.TextField(default='')
    description = models.TextField(default='')
    message_text = models.TextField(default='')
    target_username = models.CharField(max_length=225, default='')
    message_date = models.DateTimeField(editable=True)
    account = models.ForeignKey(AddAccount, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
class AvatarShareAction(models.Model):
    post_text = models.TextField(default='')
    target_post_url = models.URLField(default='')
    share_date = models.DateTimeField(editable=True)
    account = models.ForeignKey(AddAccount, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

class AvatarAddFriendAction(models.Model):
    account = models.ForeignKey(AddAccount, on_delete=models.CASCADE)
    target_username = models.CharField(max_length=225, default='')
    action_date = models.DateTimeField(editable=True)
    target_type = models.CharField(max_length=225, default='')
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)