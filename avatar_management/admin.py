from django.contrib import admin
from .models import AddAccount, AvatarProfile, AvatarPostAction, AvatarCommentAction, AvatarMessageAction,\
                    AvatarReactionAction, AvatarShareAction, AvatarAddFriendAction
# Register your models here.

admin.site.register(AddAccount)
admin.site.register(AvatarPostAction)
admin.site.register(AvatarProfile)
admin.site.register(AvatarCommentAction)
admin.site.register(AvatarMessageAction)
admin.site.register(AvatarReactionAction)
admin.site.register(AvatarShareAction)
admin.site.register(AvatarAddFriendAction)
