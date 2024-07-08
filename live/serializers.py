"""
Brief: Django serializers.py file.

Description: This file contains the serializers for the Django live app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from rest_framework import serializers
from .models import Instance, SocialUser
from django.contrib.auth.hashers import make_password


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


class SocialUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the SocialUser object.
    """
    class Meta:
        model = SocialUser
        fields = ['instance', 'user_social_type', 'first_name', 'last_name', 'username', 'password', 'has_voted', 'created_at']
        read_only_fields = ['created_at', 'user_social_type', 'username']
      
    def to_representation(self, instance):
        """
        Overriding the to_representation method to return the instance hash instead of the id.
        """
        ret = super().to_representation(instance)
        ret['instance'] = instance.instance.hash
        ret.pop('password')
        return ret
        
    def create(self, validated_data):
        """
        Overriding the create method to hash the password before saving.
        """
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Overriding the update method to hash the password if it's updated.
        """
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)