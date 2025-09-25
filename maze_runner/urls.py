from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.shortcuts import redirect
from django.urls import path, re_path, include

admin.AdminSite.site_header = settings.SITE_HEADER
admin.AdminSite.site_title = settings.SITE_TITLE

urlpatterns = [
    path('', lambda request: redirect('admin/', permanent=True)),
    path('admin/', admin.site.urls),
    path('maze/', include('maze.urls')),
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.jwt')),
]
