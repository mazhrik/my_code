from django.urls import path
from target_management import views
from rest_framework.routers import SimpleRouter

app_name = 'target_management'
router = SimpleRouter()
router.register('user_news_channels', views.UserNewsView, basename="UserNewsView")

# router.register("get", views.TargetResponsePaginated)
# urlpatterns = router.urls
urlpatterns = [
    path('query/', views.TargetSearch.as_view({'post': 'query'}), name='query_url'),
    path('fetch/again/', views.TargetSearch.as_view({'post': 'fetch_again'}), name='fetch'),
    #periodicCallTest testing endpoint 
    path('periodicCallTest/', views.TargetSearch.as_view({'get': 'periodicCallTest'}), name='fetch'),
    path('smart/', views.TargetSearch.as_view({'post': 'smart'}), name='smart_url'),
    path('bulk/', views.SocialTargetView.as_view({'post': 'create_bulk_target'}), name='create_bulk_target_url'),
    path('survey/', views.TargetSearch.as_view({'post': 'survey'}), name='survey_url'),
    path('status/', views.TargetSearch.as_view({'get': 'get_status'}), name='status_url'),
    path('updatestatus/', views.TargetSearch.as_view({'post': 'update_status'}), name='status_update_url'),
    path('fetch/', views.TargetSearch.as_view({'post': 'fetch'}), name='fetch_url'),
    path('social/view/', views.SocialTargetView.as_view({'get': 'list'}), name='social_view_url'),
    path('social/viewV1/', views.SocialTargetView.as_view({'get': 'listV1'}), name='social_viewV1_url'),
    path('gtr/view/', views.SocialTargetView.as_view({'get': 'listV2'}), name='social_viewV2_url'),
    path('social/create/', views.SocialTargetView.as_view({'post': 'create'}), name='social_create_url'),
    path('social/update/', views.SocialTargetView.as_view({'post': 'update'}), name='social_update_url'),
    path('social/delete/', views.SocialTargetView.as_view({'post': 'destroy'}), name='social_delete_url'),
    path('generic/view/', views.GenericTargetView.as_view({'get': 'list'}), name='generic_view_url'),
    path('generic/viewV1/', views.GenericTargetView.as_view({'get': 'listV1'}), name='generic_viewV1_url'),
    path('generic/create/', views.GenericTargetView.as_view({'post': 'create'}), name='generic_create_url'),
    path('generic/update/', views.GenericTargetView.as_view({'post': 'update'}), name='generic_update_url'),
    path('generic/delete/', views.GenericTargetView.as_view({'post': 'destroy'}), name='generic_delete_url'),
    path('keybase/view/', views.KeybaseTargetView.as_view({'get': 'list'}), name='generic_view_url'),
    path('keybase/viewV1/', views.KeybaseTargetView.as_view({'get': 'listV1'}), name='generic_viewV1_url'),
    path('keybase/create/', views.KeybaseTargetView.as_view({'post': 'create'}), name='generic_create_url'),
    path('keybase/update/', views.KeybaseTargetView.as_view({'post': 'update'}), name='generic_update_url'),
    path('keybase/delete/', views.KeybaseTargetView.as_view({'post': 'destroy'}), name='generic_delete_url'),
    path('get/response/', views.TargetResponse.as_view({'post': 'get_response'}), name='target_response_get'),
    path('set/response/', views.TargetResponse.as_view({'post': 'target_response'}), name='target_response'),
    path('get/linkanalysis/', views.TargetResponse.as_view({'post': 'link_analysis'}), name='link_analysis'),
    path('get/id_response/', views.TargetResponse.as_view({'post': 'response_by_id'}), name='id_response'),
    path('target_share_resource', views.TargetResponse.as_view({'post': 'target_share_resource'}), name='target_share_resource'),
    path('periodic_targets/', views.PeriodicTarget.as_view({'get': 'all_periodic_targets'}), name='periodic_target'),
    path('periodic_target/update/', views.PeriodicTarget.as_view({'patch': 'update_periodic_target'}),
         name='periodic_target_update'),

    # Social Media Account Settings
    path('socialmedia/', views.SocialMediaAccount.as_view({'get': 'list'}),
         name='socialaccount'),
    path('add_socialmedia/', views.SocialMediaAccount.as_view({'post': 'create'}),
         name='addsocialaccount'),
    path('update_socialmedia/', views.SocialMediaAccount.as_view({'post': 'update'}),
         name='updatesocialaccount'),
    path('delete_socialmedia/', views.SocialMediaAccount.as_view({'post': 'destroy'}),
         name='deletesocialaccount'),
    path('get/linkanalysis_explore/<str:gtr>', views.TargetResponse.as_view({'get': 'link_analysis_explore'}),
         name='link_analysis_explore'),
    path('get/id_response/', views.TargetResponse.as_view({'post': 'response_by_id'}), name='id_response'),
    path('get/posts/', views.TargetResponse.as_view({'post': 'get_posts'}), name='get_posts'),
    path('get/followers/', views.TargetResponse.as_view({'post': 'get_followers'}), name='get_followers'),
    path('get/followings/', views.TargetResponse.as_view({'post': 'get_following'}), name='get_followers'),
    path('delete/elasticsearch/doc/', views.TargetResponse.as_view({'post': 'delete_response_es'}),
         name='delete_response_es'),
    path('delete/hdfs/doc/', views.TargetResponse.as_view({'post': 'delete_response_hdfs'}),
         name='delete_response_hdfs'),
    path('detected_changes/', views.DetectedChanges.as_view({'get': 'detected_changes'}), name='detected_changes'),
    path('case_files/', views.file.as_view({'get': 'case_files'}), name='case_files'),
    path('keybase_files/', views.file.as_view({'get': 'keybase_files'}), name='keybase_files'),
    path('portfolio_files/', views.file.as_view({'get': 'portfolio_files'}), name='portfolio_files'),
    path('target_contributors/<str:gtr>/', views.SocialMediaAccount.as_view({'get': 'target_contributors'}), name='target_contributors'),
    path('target_available_key/<str:gtr>/', views.SocialMediaAccount.as_view({'get': 'target_available_key'}), name='target_available_key')
   
]


urlpatterns += router.urls
