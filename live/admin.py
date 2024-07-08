"""
Brief: Django admin.py file.

Description: This file contains the admin settings for the Django live app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from django.contrib import admin
from .models import Instance, SocialUser


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

class SocialUserAdmin(admin.ModelAdmin):
    """
    Custom SocialUser admin settings.
    """
    list_display = ('instance', 'user_social_type', 'first_name', 'last_name', 'username', 'password', 'has_voted', 'created_at')
    search_fields = ('first_name', 'last_name', 'username', 'instance__name', 'instance__hash')
    list_filter = ('has_voted', 'created_at', 'user_social_type')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Social User Information', {
            'fields': ('instance', 'user_social_type', 'first_name', 'last_name', 'username', 'password', 'has_voted')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
        
    )
    # list_editable = ('has_voted', 'first_name', 'last_name', 'username', 'password')
    
admin.site.register(Instance, InstanceAdmin)
admin.site.register(SocialUser, SocialUserAdmin)
