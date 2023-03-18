import django_eventstream
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views

app_name = 'core_management'
router = SimpleRouter()
router.register('imageAnalysisFRS', views.ImageAnalysisFRSViewSet, basename="imageAnalysisFRS")
router.register('log_history_view', views.LogHistoryView, basename="LogHistoryView")

urlpatterns = [
    # Tools urls
    path('identity/', views.ToolsView.as_view({'post': 'identity'}), name='identity_generator'),
    path('all_identity/', views.ToolsView.as_view({'get': 'all_fake_identities'}), name='all_fake_identities'),
    path('delete_identity/<str:id>/', views.ToolsView.as_view({'delete': 'delete_fake_identity'}), name='delete_fake_identity'),
    path('dark/', views.ToolsView.as_view({'post': 'dark'}), name='dark_web'),
    path('scrappers/', views.ToolsView.as_view({'post': 'scrappers'}), name='scrappers'),
    path('text/', views.ToolsView.as_view({'post': 'text'}), name='text_processing'),
    # News urls
    path('news/top/', views.NewsView.as_view({'post': 'top_news'}), name='top_news'),
    path('news/crawl/', views.NewsView.as_view({'post': 'top_news_crawl'}), name='crawl_news'),
    path('news/search/', views.NewsView.as_view({'post': 'get_news_search'}), name='news_search'),
    # path('text/', views.ToolsView.as_view({'post': 'text'}), name='text_processing'),

    # Twitter urls
    path('twitter/locationphrase/', views.TwitterTools.as_view({'post': 'phrase_near_location'}),
         name='twitter_location'),
    path('twitter/withinmile/', views.TwitterTools.as_view({'post': 'near_location_within_miles'}),
         name='twitter_near_location'),
    path('twitter/phrase/', views.TwitterTools.as_view({'post': 'phrase_search'}), name='twitter_phrase'),
    path('twitter/sentiment/', views.TwitterTools.as_view({'post': 'sentiments'}), name='twitter_sentiments'),
    path('twitter/tweets_search/', views.TwitterTools.as_view({'post': 'tweets_search'}), name='tweets_search'),

    # Ip Tools urls
    path('lookup/ipshort/', views.LookupTools.as_view({'post': 'ip_short'}), name='twitter_location'),
    path('lookup/imagereverse/', views.LookupTools.as_view({'post': 'image_reverse_lookup'}),
         name='twitter_near_location'),
    path('lookup/domainipinfo/', views.LookupTools.as_view({'post': 'domain_ip_info'}), name='domain_ip_info'),
    path('lookup/domaininfo/', views.LookupTools.as_view({'post': 'domain_info'}), name='domain_info'),
    path('lookup/tagoriginator/', views.LookupTools.as_view({'post': 'tag_response'}), name='tag_originator'),
    path('ip_logger/', views.IP_Logger.as_view({'post': 'ip_logger'}), name='ip_logger'),
    path('get/ip_logger/', views.IP_Logger.as_view({'get': 'get_ip_logger'}), name='get_ip_logger'),
    path('delete/ip_logger/<int:id>/', views.IP_Logger.as_view({'delete': 'delete_ip_logger'}), name='delete_ip_logger'),
    
    # amcharts urls
    path('charts/social', views.RecentTarget.as_view({'get': 'list'}, name='social_charts')),
    path('charts/targets', views.Targets.as_view({'get': 'list'}, name='targets')),
    path('charts/all', views.CountAll.as_view({'get': 'list'}, name='Count')),
    path('charts/monthly_target', views.RecentTarget.as_view({'get': 'list'}, name='social_charts')),
    # Ip Tools urls
    path('lookup/ipshort/', views.LookupTools.as_view({'post': 'ip_short'}), name='twitter_location'),
    path('lookup/imagereverse/', views.LookupTools.as_view({'post': 'image_reverse_lookup'}),
         name='twitter_near_location'),
    path('lookup/domainipinfo/', views.LookupTools.as_view({'post': 'domain_ip_info'}), name='domain_ip_info'),
    path('lookup/domaininfo/', views.LookupTools.as_view({'post': 'domain_info'}), name='domain_info'),
    path('lookup/tagoriginator/', views.LookupTools.as_view({'post': 'tag_response'}), name='tag_originator'),

    path('trends/reddit/', views.BigView.as_view({'get': 'reddit_trends'}), name='reddit_trends'),
    path('trends/youtube/', views.BigView.as_view({'get': 'youtube_trends'}), name='youtube_trends'),
    path('trends/twitter/', views.BigView.as_view({'get': 'twitter_world_trends'}), name='twitter_world_trends'),
    path('trends/twitter/country/', views.BigView.as_view({'post': 'add_target_twitter_worldwide'}),
         name='add_target_twitter_worldwide'),
    path('trends/google/', views.BigView.as_view({'post': 'google_world_trends'}), name='google_world_trends'),
    path('trends/mark/crawler/', views.BigView.as_view({'get': 'trends_crawl'}), name='trends_crawl'),
    path('news/mark/crawler/', views.BigView.as_view({'get': 'news_crawl'}), name='trends_crawl'),
    path('trends/covid/', views.BigView.as_view({'get': 'covid_data_get'}), name='covid_api_call'),

    # notifications
    path('all_user_notification/', views.UserNotifications.as_view({'get': 'all_user_notifications'}), name='all_user_notifications'),
    path('get_notification', views.NotificationViewSet.as_view({'get': 'list'})),
    path('notifications/', views.AllNotification.as_view({'get': 'list'}), name="notifications"),
    path('notifications/<int:pk>', views.AllNotification.as_view({'post': 'update'}), name="account_notifications"),
    # path('events/', include(django_eventstream.urls), {
    #     'channels': ['notification']
    # }),
    path('report_generation/<str:from_date>/<str:to_date>/<str:category>/<str:social_media>/<str:action>/', views.Report.as_view({'get': 'report_generation'}), name='report_generation'),
    path('rapideye_osint/', views.Rapideye.as_view({'get': 'rapideye_response'}), name='rapideye_response'),
    path('total_count/', views.Rapideye.as_view({'get': 'response_count'}), name='response_count'),
    path('crawler_status/', views.CrawlersDetail.as_view({'get': 'crawler_status'}), name='crawler_status'),
    path('terminate_task/', views.CrawlersDetail.as_view({'post': 'terminate_task'}), name='terminate_task'),

    # Data Retention
    path('all_targets/', views.DataRetention.as_view({'get': 'all_targets'}), name='all_targets'),
    path('delete_target/', views.DataRetention.as_view({'delete': 'delete_by_gtr'}), name='delete_by_gtr'),
    path('update_categorization/', views.DataRetention.as_view({'post': 'update_categorization'}), name='update_categorization'),

    path('get_all_ml_models/', views.ModelTraining.as_view({'get': 'get_all_ml_models'}), name='get_all_ml_models'),
    path('get_ml_model/', views.ModelTraining.as_view({'post': 'get_ml_model'}), name='get_ml_model'),
    path('delete_ml_model/', views.ModelTraining.as_view({'post': 'delete_ml_model'}), name='delete_ml_model'),
    path('cancel_ml_model/', views.ModelTraining.as_view({'post': 'cancel_ml_model'}), name='cancel_ml_model'),
    path('closeassociates/<str:GTR>/<str:CTR>/<str:target_type>/<str:target_subtype>/', views.ModelTraining.as_view({'get': 'closeassociates'}), name='closeassociates'),
    path('delete_frs/<str:title>/', views.ModelTraining.as_view({'get': 'delete_frs'}), name='delete_frs'),
    path('deploy_model/', views.ModelTraining.as_view({'post': 'deploy_model'}), name='deploy_model'),
    path('discard_model/', views.ModelTraining.as_view({'post': 'discard_model'}), name='discard_model'),
    path('automl_notify/', views.ModelTraining.as_view({'post': 'automl_notify'}), name='automl_notify'),
    path('get_image_analysis_FRS/', views.ModelTraining.as_view({'get': 'get_image_analysis_FRS'}), name='get_image_analysis_FRS'),

    path('update_sentiment/', views.DataRetention.as_view({'post': 'update_sentiment'}), name='update_sentiment'),
    path('update_additional_post_comment/', views.DataRetention.as_view({'post': 'update_additional_post_comment'}), name='update_additional_post_comment'),
    path('get_twitter_top_ten_user/', views.DataRetention.as_view({'post': 'get_twitter_top_ten_user_view'}), name='get_twitter_top_ten_user_view'),
    # Dashboard

     # path('dashboard/', views.Dashboard.as_view({'get':'dashboard_list'}, name='dashboard')),
     path("get_user_log/", views.LogView.as_view({'get':'get_user_log'}), name='get_user_log'),

    path('model/training/', views.ModelTraining.as_view({'post': 'model_training'}), name='model_training'),
    path('auto_model/training/', views.ModelTraining.as_view({'post': 'hdfs_fileupload'}), name='hdfs_fileupload'),

    # Dashboards
    path('dashboard/', views.Dashboards.as_view({'get': 'superuser_dashboard'}), name='superuser_dashboard'),
    path('tmo_dashboard/', views.Dashboards.as_view({'get': 'TMO_dashboard'}), name='TMO_dashboard'),
    path('simple_dashboard/', views.Dashboards.as_view({'get': 'simple_dashboard'}), name='simple_dashboard'),
    path('sftp_delete/<str:gtr>/', views.Sftp.as_view({'get': 'sftp_delete'}), name='sftp_delete'),
    # path('sample/', views.Dashboards.as_view({'get': 'sample'}), name='sample')
    path('ml_model/', views.BigView.as_view({'get': 'func_get_ml_model'}), name='get_ml_model'),
    path('file_upload_for_training/', views.ModelTraining.as_view({'post': 'training_keybase'}), name='training_keybase'),
    #file_upload_for_training
#     path('file_upload_for_training/', views.ModelTraining.as_view({'post': 'file_upload_for_training'}), name='file_upload_for_training'),
]


urlpatterns += router.urls
