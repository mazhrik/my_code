from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (KeybaseViewSet,
                    KeybaseReport)
from . import views

app_name = 'keybase_management'

router = SimpleRouter()
router.register('',KeybaseViewSet,basename='Keybase')

urlpatterns = [
    path('get/report/<int:id>/<str:GTR>/<int:limit>', views.KeybaseReport, name='keybase_report_generation'),
    path('keybase_filter/', KeybaseViewSet.as_view({'post': 'keybase_filter'}), name='keybase_filter'),
    path('keybase_details/<int:id>', KeybaseViewSet.as_view({'get': 'keybase_details'}), name='keybase_details'),
    # path('keybase_available_key/<str:gtr>', KeybaseViewSet.as_view({'get': 'keybase_available_key'}), name='keybase_available_key')
    path('dummyapi/', KeybaseViewSet.as_view({'post': 'dummyapi'}), name='dummyapi')
   
]

urlpatterns += router.urls