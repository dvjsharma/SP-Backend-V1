"""
Brief: Django views.py file.

Description: This file contains the views for the Django live app.

Author: Divij Sharma <divijs75@gmail.com>
"""

import datetime
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Instance
from .serializers import InstanceSerializer


class IsOwner(permissions.BasePermission):
    """
    Custom permission class
    """
    def has_object_permission(self, request, obj):
        """
        Check if the user is the owner of the instance object.
        """
        return obj.user == request.user


class InstanceListCreateView(generics.ListCreateAPIView):
    """
    List and create view for the Instance object.
    """
    serializer_class = InstanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filters the instances for the current user.
        """
        return Instance.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Save the instance object with the user field set to the current user.
        """
        serializer.save(user=self.request.user)


class InstanceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update and destroy view for the Instance object.
    """
    serializer_class = InstanceSerializer
    lookup_field = 'hash'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filters the instances for the current user.
        """
        return Instance.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        """
        If the user is the owner of the instance object, save the instance object.
        """
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this instance.")
        serializer.save(last_modified=datetime.datetime.now())

    def perform_destroy(self, instance):
        """
        If the user is the owner of the instance object, delete the instance object.
        """
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this instance.")
        instance.delete()