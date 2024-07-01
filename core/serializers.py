"""
Brief: Django serializers.py file.

Description: This file contains the serializers for the Django core app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

user = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Serializer for creating a new user.
    """
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password', 'first_name', 'last_name',
                  'email']


class UserSerializer(BaseUserSerializer):
    """
    Serializer for handling user data.
    """
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'first_name', 'last_name', 'email', 'username',
                  'is_active', 'is_deactivated']

    def validate(self, attrs):
        """
        Validate the user data.

        - Check if the username exists in the validated attributes.
        - Ensure the user is not deactivated or inactive.
        """
        validated_data = super().validate(attrs)
        instance = self.instance

        if instance:
            username = validated_data.get('username', instance.username)
            try:
                user_instance = user.objects.get(username=username)
            except user.DoesNotExist:
                raise ValidationError('User not found')

            if user_instance.is_deactivated:
                raise ValidationError('Account deactivated')

            if not user_instance.is_active:
                raise ValidationError('Account not activated')

        return validated_data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer for obtaining JWT tokens.
    """
    def validate(self, attrs):
        """
        Validate the token data and add additional user information to the token payload.

        - Include user's id, first name, last name, email, username, is_active, and is_deactivated status.
        """
        data = super().validate(attrs)

        obj = self.user

        data.update({
            'id': obj.id, 'first_name': obj.first_name,
            'last_name': obj.last_name, 'email': obj.email,
            'username': obj.username,
            'is_active': obj.is_active,
            'is_deactivated': obj.is_deactivated,
        })
        return data
