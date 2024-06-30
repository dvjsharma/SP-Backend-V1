"""
Brief: Django urls.py file.

Description: This file contains the URL patterns for the Django project.

Author: Divij Sharma <divijs75@gmail.com>
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
