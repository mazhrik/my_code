from target_management.constants import TARGET_SUB_TYPE
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Notification(models.Model):
    """
    Model for Notificationss
    """
    Notification_message = models.CharField(max_length=80)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource_url = models.URLField()
    read_status = models.BooleanField()
    class Meta:

            permissions = [
            ("tools_permission", "tools permission"),
            ("news_permission","news permission"),
            ("history_permission","history permission"),
            ("report_generation_in_tools","report generation in tools")
            ]

    def __str__(self):
        return self.Notification_message


class FakeIdentity(models.Model):
    data = models.JSONField(default={})
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class IPLogger(models.Model):
    city = models.CharField(max_length=225, default='')
    country = models.CharField(max_length=225, default='')
    domain_name = models.CharField(max_length=225, default='')
    isp = models.CharField(max_length=225, default='')
    region = models.CharField(max_length=225, default='')
    ip_add = models.CharField(max_length=225, default='')
    time = models.CharField(max_length=225, default='')
    user_agent = models.CharField(max_length=225, default='')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_on',)

class Log(models.Model):
    request_username  = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    request_method = models.CharField(max_length=50)
    request_url = models.CharField(max_length=255)
    request_time = models.DateTimeField(auto_now_add=True)
    request_data = models.JSONField(default=dict)
    # response_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = ("Log")
        verbose_name_plural = ("Logs")
        ordering = ('-request_time',)

    def __str__(self):
        return self.request_username.username

class Log_history(models.Model):
    request_username  = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    request_method = models.CharField(max_length=50)
    request_url = models.CharField(max_length=255)
    request_time = models.DateTimeField(auto_now_add=True)
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    ip = models.CharField(max_length=255, null=True)
    


    class Meta:
        verbose_name = ("Log_history")
        verbose_name_plural = ("Log_histories")
        ordering = ('-request_time',)

    def __str__(self):
        return self.request_username.username

class NewsMonitoring(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.CharField(max_length=225)


class AutoML(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=225)
    upload_on = models.DateTimeField(auto_now_add=True)
    model_name = models.CharField(default="",max_length=225)
    message = models.CharField(default="Job Queued",max_length=225)
    status = models.CharField(default="IN_PROGRESS",max_length=225)
    type = models.CharField(default="CATEGORIZATION",max_length=225)

class ImageAnalysisFRS(models.Model):
    title = models.CharField(max_length=225, unique=True)
    image_url = models.URLField(default='', max_length=5000)
    target_type = models.CharField(max_length=225, default="")
    target_subtype = models.CharField(max_length=225, default="")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title