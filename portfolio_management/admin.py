from django.contrib import admin
from .models import Individual, Group, LinkedData, Event

# Register your models here.


admin.site.register(Individual)
admin.site.register(Group)
admin.site.register(LinkedData)
admin.site.register(Event)
