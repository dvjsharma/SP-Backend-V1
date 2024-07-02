"""
Brief: Django admin.py file.

Description: This file contains the admin settings for the Django core app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from django.contrib import admin
from .models import User


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active',
                    'is_deactivated', 'is_superuser')


admin.site.register(User, CustomUserAdmin)
