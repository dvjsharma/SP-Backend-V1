"""
Brief: Django urls.py file.

Description: This file contains the URL patterns for the Django live app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from django.urls import path
from .views import InstanceListCreateView, InstanceRetrieveUpdateDestroyView, InstanceTypeStatusView

urlpatterns = [
    path('instance/', InstanceListCreateView.as_view(), name='instance-list-create'),
    path('instance/<str:hash>/', InstanceRetrieveUpdateDestroyView.as_view(), name='instance-detail'),
    path('instance/info', InstanceTypeStatusView.as_view(), name='instance-status'),
]
