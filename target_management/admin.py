from django.contrib import admin
from .models import (SocialTarget,
                     KeybaseTarget,
                     GenericTarget)

# Register your models here.

admin.site.register(SocialTarget)
admin.site.register(KeybaseTarget)
admin.site.register(GenericTarget)
