"""
Brief: Django apps.py file.

Description: This file contains the app configuration for the Django data app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from django.apps import AppConfig


class DataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data"
