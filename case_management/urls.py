from os import name
from rest_framework.routers import SimpleRouter
from django.urls import path, include
from .views import (CaseViewSet,
                    LeakedDataViewSet,
                    LocationViewSet,
                    PersonViewSet,
                    InvestigatorViewSet,
                    EvidenceViewSet,
                    MediaViewSet,
                    UserViewSet, CaseInvestigationMapViewSet,
                    EventViewSet, ShapeViewSet, CaseReportGeneration)

app_name = 'case_management'

router = SimpleRouter()
router.register("location", LocationViewSet, basename='location')
router.register("person", PersonViewSet)
router.register("investigator", InvestigatorViewSet)
router.register("evidence", EvidenceViewSet)
router.register("media", MediaViewSet)
router.register("user", UserViewSet)
router.register("cib", CaseInvestigationMapViewSet)
# router.register('event', EventViewSet)
router.register('shape', ShapeViewSet)
urlpatterns = [
    path('info/', include(router.urls)),
    path('case_detail/<str:id>/', CaseViewSet.as_view({'get': 'case_detail'}), name='case_detail'),
    path('view/', CaseViewSet.as_view({'get': 'list'}), name='case_view_url'),
    path('viewV1/', CaseViewSet.as_view({'get': 'listV1'}), name='case_viewV1_url'),
    path('add/investigator/', CaseViewSet.as_view({'post': 'attach_investigator'}), name='attach_investigator'),
    path('remove/investigator/', CaseViewSet.as_view({'post': 'deattach_investigator'}), name='deattach_investigator'),
    path('add/person/', CaseViewSet.as_view({'post': 'attach_person'}), name='attach_person'),
    path('add/location/', CaseViewSet.as_view({'post': 'attach_location'}), name='attach_location'),
    path('add/media/', CaseViewSet.as_view({'post': 'attach_media'}), name='attach_media'),
    path('add/evidence/', CaseViewSet.as_view({'post': 'attach_evidence'}), name='attach_evidence'),
    path('add/event/', CaseViewSet.as_view({'post': 'attach_event'}), name='attach_event'),
    path('add/data/', CaseViewSet.as_view({'post': 'link_data'}), name='link_data'),
    path('create/', CaseViewSet.as_view({'post': 'create'}), name='case_create_url'),
    path('update/', CaseViewSet.as_view({'post': 'update'}), name='case_update_url'),
    path('delete/', CaseViewSet.as_view({'get': 'destroy'}), name='case_delete_url'),
    path('upload/', CaseViewSet.as_view({'post': 'simple_upload'}), name='upload'),
    path('create_event/', EventViewSet.as_view({'post': 'create_event'}), name='create_event'),
    path('update_event/', EventViewSet.as_view({'patch': 'update_event'}), name='update_event'),
    path('delete_event/<int:id>/', EventViewSet.as_view({'delete': 'delete_event'}), name='delete_event'),
    path('generate_commentors/', CaseReportGeneration.as_view({'get': 'generate_commentors_classification_report_cms'}), name='generate_commentors'),
    path('active_users/', CaseReportGeneration.as_view({'get': 'generate_active_users_report'}), name='generate_active_users_report'),
    path('case_filter/', CaseViewSet.as_view({'post': 'case_filter'}), name='case_filter'),
    path('details/<int:id>/', CaseViewSet.as_view({'get': 'details'}), name='details'),
    path('get_tao_investigator/', CaseViewSet.as_view({'get': 'get_tao_investigator'}), name='get_tao_investigator'),
    path('leaked_data_upload/', LeakedDataViewSet.as_view({'post': 'leaked_data_upload'}), name='leaked_data_upload'),
    path('leaked_data/', LeakedDataViewSet.as_view({'post': 'leaked_data'}), name='leaked_data'),
    path('leaked_data_view/', LeakedDataViewSet.as_view({'get': 'leaked_data_view'}), name='leaked_data_view'),
    path('leaked_data_delete/<int:id>/', LeakedDataViewSet.as_view({'delete': 'leaked_data_delete'}), name='leaked_data_delete'),
    
]
urlpatterns += router.urls
