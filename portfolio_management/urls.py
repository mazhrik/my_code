from portfolio_management import views
from rest_framework.routers import SimpleRouter
from keybase_management.views import KeybaseViewSet
from django.urls import path
app_name = 'portfolio_management'

router = SimpleRouter()
router.register("individual", views.IndividualViewSet,basename='Individual')
router.register("group", views.GroupViewSet,basename='Group')
router.register("event", views.EventViewSet,basename='Event')
router.register("linked_data", views.LinkedDataViewsets)
router.register("keybase", KeybaseViewSet,basename='Keybase')
router.register("user", views.UserViewSet)
urlpatterns = router.urls

urlpatterns += [
    path('all_portfolio/', views.IndividualViewSet.as_view({'post': 'all_portfolio'}), name='all_portfolio'),
    path('portfolio_pagination/', views.IndividualViewSet.as_view({'get': 'portfolio_pagination'}), name='portfolio_pagination'),
    path('attach/keybase/', views.IndividualViewSet.as_view({'post': 'attach_keybase'}), name='attach_keybase'),
    path('attach/target/', views.IndividualViewSet.as_view({'post': 'attach_target'}), name='attach_target'),
    path('portfolio_report/<int:id>', views.EventViewSet.as_view({'get': 'portfolio_report'}), name='portfolio_report'),
    path('attach/portfolio/', views.IndividualViewSet.as_view({'post': 'attach_portfolio'}), name='attach_portfolio'),
    path('attach/case/', views.IndividualViewSet.as_view({'post': 'attach_case'}), name='attach_case'),
    path('attach/data/', views.IndividualViewSet.as_view({'post': 'link_data'}), name='link_data'),
    path('portfolio_detail/<str:type>/<str:id>/', views.IndividualViewSet.as_view({'get': 'portfolio_detail'}),
         name='portfolio_detail')
]
