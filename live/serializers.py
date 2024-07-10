"""
Brief: Django serializers.py file.

Description: This file contains the serializers for the Django live app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from rest_framework import serializers
from social_core import exceptions
from social_django.utils import load_backend, load_strategy
from django.contrib.auth.hashers import make_password
from .models import Instance, SocialUser
from .token import jwt


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
        fields = ['instance', 'user_social_type', 'first_name', 'last_name',
                  'username', 'password', 'has_voted', 'created_at']
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


class SocialUserLoginSerializer(serializers.Serializer):
    """
    Serializer for the SocialUser login object.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class CustomProviderAuthSerializer(serializers.Serializer):
    """
    Serializer for the custom provider authentication (Google)
    """
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = serializers.CharField(read_only=True)

    def create(self, validated_data):
        """
        Obtain the JWT token for the user.
        """
        user = validated_data["user"]
        return jwt.TokenStrategy.obtain(user)

    def validate(self, attrs):
        """
        Validate the serializer data.
        """
        request = self.context["request"]
        if "state" in request.GET:
            self._validate_state(request.GET["state"])

        strategy = load_strategy(request)
        redirect_uri = strategy.session_get("redirect_uri")

        backend_name = self.context["view"].kwargs["provider"]
        backend = load_backend(strategy=strategy, name=backend_name, redirect_uri=redirect_uri)

        try:
            user = backend.auth_complete()
            social_user = self.get_or_create_social_user(user)
        except exceptions.AuthException as e:
            raise serializers.ValidationError(str(e))
        return {"user": social_user}

    def get_or_create_social_user(self, user):
        """
        Create a social user if it doesn't exist or return the existing one.
        """
        instance = Instance.getExistingInstance(self.context.get("hash"))
        try:
            social_user = SocialUser.objects.get(username=user.email)
        except SocialUser.DoesNotExist:
            social_user = SocialUser.objects.create(
                instance=instance,
                user_social_type=0x1 << 0,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.email,
                password=make_password(user.password),
            )
        return social_user

    def _validate_state(self, value):
        """
        Validate the state parameter sent via OAuth request.
        """
        request = self.context["request"]
        strategy = load_strategy(request)
        redirect_uri = strategy.session_get("redirect_uri")

        backend_name = self.context["view"].kwargs["provider"]
        backend = load_backend(strategy=strategy, name=backend_name, redirect_uri=redirect_uri)

        try:
            backend.validate_state()
        except exceptions.AuthMissingParameter:
            raise serializers.ValidationError("State could not be found in request data.")
        except exceptions.AuthStateMissing:
            raise serializers.ValidationError("State could not be found in server-side session data.")
        except exceptions.AuthStateForbidden:
            raise serializers.ValidationError("Invalid state has been provided.")

        return value
