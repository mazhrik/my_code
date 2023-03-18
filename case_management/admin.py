from django.contrib import admin
from case_management.models import (Case,
                                    Location,
                                    Person,
                                    Investigator,
                                    Evidence,
                                    Media, CaseInvestigationMap,
                                    Shape, Event)

# Register your models here.

admin.site.register(Case)
admin.site.register(Location)
admin.site.register(Person)
admin.site.register(Investigator)
admin.site.register(Evidence)
admin.site.register(Media)
admin.site.register(CaseInvestigationMap)
admin.site.register(Shape)
admin.site.register(Event)
