"""
Brief: Django urls.py file.

Description: This file contains the URL patterns for the Django data app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from django.urls import path
from .views import FormListCreateView, FormDetailView
from .views import QuestionListCreateView, QuestionDetailView
from .views import ResponseListCreateView, ResponseDetailView
from .views import custom_get_method, custom_post_method

urlpatterns = [
    path('<str:hash>/form/', FormListCreateView.as_view(), name='form-list-create'),
    path('<str:hash>/form/<int:pk>', FormDetailView.as_view(), name='form-detail'),
    path('<str:hash>/form/<int:pk>/question', QuestionListCreateView.as_view(), name='question-list-create'),
    path('<str:hash>/form/<int:pk>/question/<int:itempk>', QuestionDetailView.as_view(), name='question-detail'),
    path('<str:hash>/responses/', ResponseListCreateView.as_view(), name='response-list-create'),
    path('<str:hash>/responses/<int:pk>', ResponseDetailView.as_view(), name='response-detail'),
    path('<str:hash>/voter/get-data', custom_get_method, name='form-get'),
    path('<str:hash>/voter/post-data', custom_post_method, name='form-post'),
]
