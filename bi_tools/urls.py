from django.urls import path
from bi_tools.views import BiTools


urlpatterns = [
    path('get_query/', BiTools.as_view({'get': 'list'}), name='get_query'),
    # path('query_response/', BiTools.as_view({'get': 'query_response'}), name='query_response'),
]
