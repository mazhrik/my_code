"""OCS_Rest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from OCS_Rest import settings

from multiprocessing import Process
# from core_management.consumer import main
#
# # from core_management.rabbit_thread import Rabbit_Consumer
#
# # try:
# #     subprocess.Popen(['ocsrest/bin/python3', '-u', 'core_management/consumer.py'])
# #     print("done")
# # except Exception as e:
# #     print('----------', e, '---------------')
#
# # consumer = Rabbit_Consumer(1)
# # consumer.start()
# p = Process(target=main)
# p.start()

from rest_framework.documentation import include_docs_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('v1/target/', include('target_management.urls', namespace='v1')),
    path('v1/core/', include('core_management.urls', namespace='v1')),
    path('v1/case/', include('case_management.urls', namespace='v1')),
    path('v2/case/', include('case_management.urls', namespace='v2')),
    path('v1/account/', include('account_management.urls', namespace='v1')),  # Version support
    path('v2/account/', include('account_management.urls', namespace='v2')),  # Version support
    path('v1/keybase/', include('keybase_management.urls', namespace='v1')),
    path('v1/portfolio/', include('portfolio_management.urls', namespace='v1')),
    path('v2/portfolio/', include('portfolio_management.urls', namespace='v2')),
    path('v1/bi_tools/', include('bi_tools.urls')),
    path('v1/avatar/', include('avatar_management.urls')),
    path('v1/report/', include('report_management.urls')),
    path('docs/', include_docs_urls(title='owl sense', public=False))

]

if settings.SERVER == 'DEV':
    import debug_toolbar
    urlpatterns += [
        path(r'^__debug__/', include(debug_toolbar.urls)),
    ]

