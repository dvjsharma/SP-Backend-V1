"""
Brief: Django urls.py file.

Description: This file contains the URL patterns for the Django data app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from django.urls import path
from .views import FormListCreateView, FormDetailView
from .views import QuestionListCreateView, QuestionDetailView
from .views import AnswerListCreateView, AnswerDetailView
from .views import custom_get_method

urlpatterns = [
    path('<str:hash>/form/', FormListCreateView.as_view(), name='form-list-create'),
    path('<str:hash>/form/<int:pk>', FormDetailView.as_view(), name='form-detail'),
    path('<str:hash>/form/<int:pk>/question', QuestionListCreateView.as_view(), name='question-list-create'),
    path('<str:hash>/form/<int:pk>/question/<int:itempk>', QuestionDetailView.as_view(), name='question-detail'),
    path('<str:hash>/answers/', AnswerListCreateView.as_view(), name='answer-list-create'),
    path('<str:hash>/answers/<int:pk>', AnswerDetailView.as_view(), name='answer-detail'),
    path('<str:hash>/voter/form', custom_get_method, name='form-get'),
]
