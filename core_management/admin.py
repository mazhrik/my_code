from django.contrib import admin
from .models import Notification, FakeIdentity, IPLogger, NewsMonitoring, AutoML
# Register your models here.

admin.site.register(Notification)
admin.site.register(FakeIdentity)
admin.site.register(IPLogger)
admin.site.register(NewsMonitoring)
admin.site.register(AutoML)
