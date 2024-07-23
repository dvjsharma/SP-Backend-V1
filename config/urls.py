"""
Brief: Django urls.py file.

Description: This file contains the URL patterns for the Django project.

Author: Divij Sharma <divijs75@gmail.com>
"""
import os
from django.contrib import admin
from django.urls import path, include

API_BASE_PATH = "api/v1/"

urlpatterns = [
    path(f"{API_BASE_PATH}auth/", include("core.urls")),
    path(f"{API_BASE_PATH}live/", include("live.urls")),
    path(f"{API_BASE_PATH}data/", include("data.urls")),
]

if os.environ.get("ENV") == "development":
    urlpatterns.append(path("admin/", admin.site.urls))
