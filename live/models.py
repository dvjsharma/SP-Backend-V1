"""
Brief: Django models.py file.

Description: This file contains the models for the Django live app.

Author: Divij Sharma <divijs75@gmail.com>
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Instance(models.Model):
    """
    Model for the Instance object.
    """
    TYPE_CHOICES = (
        (0x1 << 0, 'Open to All'),
        (0x1 << 1, 'Open within Ogranization'),
        (0x1 << 2, 'Open to Specific Users'),
    )

    STATUS_CHOICES = (
        (0x1 << 0, 'Closed'),
        (0x1 << 1, 'Open'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    instance_auth_type = models.IntegerField(choices=TYPE_CHOICES, default=0x1 << 0)
    name = models.CharField(max_length=100)
    description = models.TextField()
    instance_status = models.IntegerField(choices=STATUS_CHOICES, default=0x1 << 1)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    hash = models.CharField(max_length=16, unique=True, editable=False)

    def __str__(self):
        """
        Return the name of the instance object.
        """
        return self.name

    def save(self, *args, **kwargs):
        """
        Save the instance object if the hash is not present (for POST requests).
        """
        if not self.hash:
            self.hash = uuid.uuid4().hex[:16]
        super().save(*args, **kwargs)
