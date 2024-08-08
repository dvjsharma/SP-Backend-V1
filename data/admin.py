"""
Brief: Django admin.py file.

Description: This file contains the admin settings for the Django data app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from django.contrib import admin
from .models import Skeleton, Field, Response, Answer


class SkeletonAdmin(admin.ModelAdmin):
    """
    Custom Skeleton admin settings.
    """
    list_display = ('title', 'instance', 'description', 'created_at', 'endMessage')
    search_fields = ('title', 'endMessage')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Skeleton Info', {
            'fields': ('instance', 'title', 'description', 'endMessage')
        }),
        ('Dates', {
            'fields': ('created_at',)
        }),
    )


class FieldAdmin(admin.ModelAdmin):
    """
    Custom Field admin settings.
    """
    list_display = ('title', 'type', 'required', 'skeleton')
    search_fields = ('title', 'type')
    list_filter = ('type', 'required')
    ordering = ('skeleton', 'title')
    fieldsets = (
        ('Field Info', {
            'fields': ('skeleton', 'title', 'type', 'required')
        }),
        ('Options', {
            'fields': ('options', 'accepted')
        }),
    )


class ResponseAdmin(admin.ModelAdmin):
    """
    Custom Response admin settings.
    """
    list_display = ('skeleton', 'submitted_at', 'user')
    search_fields = ('skeleton__title', 'user__username')
    list_filter = ('submitted_at', 'user')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at',)
    fieldsets = (
        ('Response Info', {
            'fields': ('skeleton', 'submitted_at', 'user')
        }),
    )

    def get_queryset(self, request):
        """
        Customize the queryset to include related fields.
        """
        queryset = super().get_queryset(request)
        return queryset.select_related('skeleton', 'user')


class AnswerAdmin(admin.ModelAdmin):
    """
    Custom Answer admin settings.
    """
    list_display = ('response', 'field', 'value')
    search_fields = ('response__skeleton__title', 'field__title', 'value')
    list_filter = ('field', 'response__skeleton')
    ordering = ('response', 'field')
    fieldsets = (
        ('Answer Info', {
            'fields': ('response', 'field', 'value')
        }),
    )

    def get_queryset(self, request):
        """
        Customize the queryset to include related fields.
        """
        queryset = super().get_queryset(request)
        return queryset.select_related('response', 'field')


admin.site.register(Skeleton, SkeletonAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(Answer, AnswerAdmin)
