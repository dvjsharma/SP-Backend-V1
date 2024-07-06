"""
Brief: Django serializers.py file.

Description: This file contains the serializers for the Django live app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from rest_framework import serializers
from .models import Instance


class InstanceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Instance object.
    """
    class Meta:
        model = Instance
        fields = ['user', 'instance_auth_type', 'name', 'description', 'instance_status',
                  'created_at', 'last_modified', 'hash']
        read_only_fields = ['hash', 'created_at', 'last_modified', 'user']

    def create(self, validated_data):
        """
        Create the instance object with the user field set to the current user.
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
