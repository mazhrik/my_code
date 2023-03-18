from django.db import models

# Create your models here.


class ReportsNotes(models.Model):
    report_id = models.CharField(max_length=225, default='')
    type = models.CharField(max_length=225, default='')
    username = models.CharField(max_length=225)
    note = models.CharField(max_length=500, default='')
    date = models.DateTimeField(auto_now_add=True)
   

    class Meta:
 
        permissions = [
            ("can_download_report", "can download report")
            ] 


class Brief(models.Model):
    report_id = models.CharField(max_length=225, default='')
    type = models.CharField(max_length=225, default='')
    username = models.CharField(max_length=225)
    brief = models.CharField(max_length=500, default='')
    date = models.DateTimeField(auto_now_add=True)
    