from django.urls import path
from . import views

urlpatterns = [
    path('add/notes/', views.ReportNotesView.as_view({'post': 'add_notes'}), name='add_notes'),
    path('get/notes/', views.ReportNotesView.as_view({'post': 'get_notes'}), name='get_notes'),
    path('add/briefs/', views.BriefView.as_view({'post': 'add_briefs'}), name='add_briefs'),
    path('get/briefs/', views.BriefView.as_view({'post': 'get_briefs'}), name='get_briefs'),
    path('contributors/', views.ReportNotesView.as_view({'get': 'contributors'}), name='contributors'),
]
