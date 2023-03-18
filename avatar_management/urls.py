from django.urls import path
from avatar_management import views

urlpatterns = [
    path('add_profile/', views.Avatar.as_view({'post': 'add_profile'}), name='add_profile'),
    path('add_account/', views.Avatar.as_view({'post': 'add_account'}), name='add_account'),
    path('delete_account/', views.Avatar.as_view({'delete': 'delete_account'}), name='delete_account'),
    path('post_action/', views.Avatar.as_view({'post': 'post_avatar_action'}), name='post_action'),
    path('comment_action/', views.Avatar.as_view({'post': 'comment_avatar_action'}), name='comment_action'),
    path('reaction_action/', views.Avatar.as_view({'post': 'reaction_avatar_action'}), name='reaction_post'),
    path('share_action/', views.Avatar.as_view({'post': 'share_avatar_action'}), name='share_action'),
    path('message_action/', views.Avatar.as_view({'post': 'message_avatar_action'}), name='message_action'),
    path('action/addfriend/', views.Avatar.as_view({'post': 'addfriend_avatar_action'}), name='addfriend_avatar_action'),
    path('all_accounts/', views.Avatar.as_view({'get': 'all_accounts'}), name='all_accounts'),
    # path('success_rate/<int:id>', views.Avatar.as_view({'get': 'success_rate'}), name='success_rate'),
    path('all_profiles/', views.Avatar.as_view({'get': 'all_profiles'}), name='all_profiles'),
    path('fetch_profile/', views.Avatar.as_view({'post': 'fetch_profiles'}), name='fetch_profiles'),
    path('update_profile/<int:pk>/', views.Avatar.as_view({'put': 'update_profile'}), name='update_profile'),
    path('delete_profile/<int:pk>/', views.Avatar.as_view({'delete': 'delete_profile'}), name='delete_profile'),
    path('action/archive/', views.Avatar.as_view({'get': 'schedule_actions_archive'}), name='schedule_actions_archive'),
    path('update_account/', views.Avatar.as_view({'post': 'update_avatars'}), name='update_avatars'),
    path('dashboard/', views.Avatar.as_view({'get': 'dashboard'}), name='dashboard'),
    path('social_acc_relogin/', views.Avatar.as_view({'post': 'social_acc_relogin'}), name='social_acc_relogin')
    
]
