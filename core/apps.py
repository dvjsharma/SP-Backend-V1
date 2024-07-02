"""
Brief: Django apps.py file.

Description: This file contains the app configuration for the Django core app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
