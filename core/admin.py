"""
Brief: Django admin.py file.

Description: This file contains the admin settings for the Django core app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from django.contrib import admin
from .models import User


class CustomUserAdmin(admin.ModelAdmin):
    """
    Custom User admin settings.
    """
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active',
                    'is_deactivated', 'is_superuser')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_deactivated', 'is_superuser', 'date_joined')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'username', 'password')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_deactivated', 'is_superuser', 'is_staff', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    # list_editable = ('is_active', 'is_deactivated', 'is_superuser')

    actions = ['deactivate_users', 'activate_users']


admin.site.register(User, CustomUserAdmin)
