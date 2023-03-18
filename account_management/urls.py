from django.urls import path
from account_management import views
from rest_framework.routers import SimpleRouter

app_name = 'account_management'
router = SimpleRouter()
router.register('add_user', views.AddUserViewSet, basename="add_user")
router.register('add_group', views.AddGroupViewSet, basename="add_group")
router.register('add_profile', views.AddUserProfileViewSet)
# router.register('permissions', views.ViewPermissions)
router.register('addeduser', views.AddedUsers)
router.register('choosen_user', views.ChosenUser)
router.register('team', views.TeamView)
router.register('team_member', views.TeamMemmberView)
router.register('accountsettings', views.AccountSettingViewSet, basename="accountsettings")
urlpatterns = [
    path('all_users/', views.AddUserViewSet.as_view({'get': 'list'}), name='list'),
    path('create_profile/', views.AddUserProfileViewSet.as_view({'post': 'create_profile'}), name='create'),
    path('change_password/', views.AddUserViewSet.as_view({'post': 'changePassword'}), name='changePassword'),
    path('all_user_of_group/', views.AddGroupViewSet.as_view({'post': 'all_user_of_group'}), name='all_user_of_group'),
    path('edit_user_of_group/', views.AddGroupViewSet.as_view({'post': 'edit_user_of_group'}), name='edit_user_of_group'),
    path('team_member_bulk_create/', views.TeamMemmberView.as_view({'post': 'create_bulk'}), name='create_bulk'),
    path('team_member_bulk_update/<int:id>/', views.TeamMemmberView.as_view({'post': 'update_bulk'}), name='update_bulk'),
    path('get_team_and_members/<int:id>/', views.TeamMemmberView.as_view({'get': 'get_team_and_members'}), name='get_team_and_members'),
    path('profile_info/<int:id>/', views.AddUserProfileViewSet.as_view({'get': 'retrive_user'}), name='profile_info'),
    path('group_info/', views.AddGroupViewSet.as_view({'get': 'group_info'}), name='group_info'),
    path('list_of_tmo/', views.TeamView.as_view({'get': 'list_of_TMO'}), name='list_of_TMO'),
    path('list_of_other_groups/', views.TeamMemmberView.as_view({'get': 'list_of_TAO_other'}), name='list_of_TAO_other'),
    path('update_profile/<int:id>/', views.AddUserProfileViewSet.as_view({'patch': 'update_profile'}),
         name='update_profile'),
    path('all_permissions/', views.ViewPermissions.as_view({'get': 'list'}), name='list'),
#     path('team/', views.TeamView.as_view({'get': 'list'}), name='list_team'),
    path('login/', views.LoginView.as_view(), name='login_url'),
    path('logout/', views.LogoutView.as_view(), name='logout_url'),
    path('update/password/', views.AddUserViewSet.as_view({'post': 'update_one_time_password'}),
         name='update_one_time_password'),
    path('deactivate_account/', views.AccountDeactivate.as_view({'put': 'de_activate_account'}), name='de_activate_account')
]
urlpatterns += router.urls
