"""
Brief: Django admin.py file.

Description: This file contains the admin settings for the Django live app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from django.contrib import admin
from .models import Instance


class InstanceAdmin(admin.ModelAdmin):
    """
    Custom User admin settings.
    """
    list_display = ('user', 'instance_auth_type', 'name', 'description',
                    'instance_status', 'created_at', 'last_modified', 'hash')
    search_fields = ('name', 'description', 'user__username', 'hash', 'instance_auth_type')
    list_filter = ('instance_status', 'created_at', 'last_modified', 'user')
    ordering = ('-created_at',)
    readonly_fields = ('hash', 'created_at', 'last_modified')
    fieldsets = (
        ('Instance Information', {
            'fields': ('user', 'instance_auth_type', 'name', 'description')
        }),
        ('Status', {
            'fields': ('instance_status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_modified')
        }),
        ('Hash', {
            'fields': ('hash',)
        }),
    )
    # list_editable = ('instance_status', 'name', 'description')


admin.site.register(Instance, InstanceAdmin)
