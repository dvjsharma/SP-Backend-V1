"""
Brief: Django models.py file.

Description: This file contains the models for the Django core app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    Fields:
    - first_name: User's first name, required.
    - last_name: User's last name, required.
    - username: User's username, unique and required.
    - email: User's email, unique and required.
    - is_deactivated: Flag indicating if the user is deactivated, defaults to False.
    - is_active: Flag indicating if the user is active, defaults to False.
    """
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    username = models.CharField(max_length=30, unique=True, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    is_deactivated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # Note: Superuser needs to be activated manually

    def __str__(self):
        """
        Return the user's username.
        """
        return self.username

    def get_username(self):
        """
        Get the user's username.
        """
        return self.username

    def get_email(self):
        """
        Get the user's email.
        """
        return self.email

    def deactivate(self):
        """
        Deactivate the user.
        """
        self.is_deactivated = True
        self.save()

    def activate(self):
        """
        Activate the user.
        """
        self.is_deactivated = False
        self.save()
