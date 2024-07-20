"""
Brief: Django urls.py file.

Description: This file contains the URL patterns for the Django data app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from django.urls import path
from .views import FormListCreateView, FormDetailView
from .views import QuestionListCreateView, QuestionDetailView
from .views import AnswerListCreateView, AnswerDetailView

urlpatterns = [
    path('form/', FormListCreateView.as_view(), name='form-list-create'),
    path('form/<int:pk>', FormDetailView.as_view(), name='form-detail'),
    path('form/<int:pk>/question', QuestionListCreateView.as_view(), name='question-list-create'),
    path('form/<int:pk>/question/<int:itempk>', QuestionDetailView.as_view(), name='question-detail'),
    path('answers/', AnswerListCreateView.as_view(), name='answer-list-create'),
    path('answers/<int:pk>', AnswerDetailView.as_view(), name='answer-detail'),
]
