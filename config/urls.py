"""
Brief: Django urls.py file.

Description: This file contains the URL patterns for the Django project.

Author: Divij Sharma <divijs75@gmail.com>
"""
import os
from django.contrib import admin
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, include

schema_view = get_schema_view(
   openapi.Info(
      title="Survey and Polling API",
      default_version='v1',
      description="Survey and Polling backend APIs swagger documentation",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@yourapi.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

API_BASE_PATH = "api/v1/"

urlpatterns = [
    path(f"{API_BASE_PATH}auth/", include("core.urls")),
    path(f"{API_BASE_PATH}live/", include("live.urls")),
    path(f"{API_BASE_PATH}data/", include("data.urls")),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

if os.environ.get("ENV") == "development":
    urlpatterns.append(path("admin/", admin.site.urls))
