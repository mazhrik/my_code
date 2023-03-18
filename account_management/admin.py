from django.contrib import admin
from account_management.models import UserProfile, AccountSettings, UserActivity, Team, Team_members

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(AccountSettings)
admin.site.register(UserActivity)
admin.site.register(Team)
admin.site.register(Team_members)
