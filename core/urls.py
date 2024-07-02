"""
Brief: Django urls.py file.

Description: This file contains the URL patterns for the Django core app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from django.urls import path, include
from core.views import CustomTokenObtainPairView, home, check_username_exists

urlpatterns = [
    path('jwt/create', CustomTokenObtainPairView.as_view(), name='custom_jwt_create'),
    path('', include("djoser.urls")),
    path('', include("djoser.urls.jwt")),
    path('status', home, name='home'),
    path('exists', check_username_exists, name='exists'),
]
