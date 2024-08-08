"""
Brief: Django models.py file.

Description: This file contains the models for the Django data app.

Author: Divij Sharma <divijs75@gmail.com>
"""

import json
from django.db import models
from live.models import Instance, SocialUser

TYPE_CHOICES = [
    ('short-text', 'Short answer text'),
    ('long-text', 'Long answer text'),
    ('number', 'Numeric answer'),
    ('multioption-singleanswer', 'Multiple choice single answer'),
    ('multioption-multianswer', 'Multiple choice multiple answers'),
    ('file', 'File upload'),
]


class Skeleton(models.Model):
    """
    A model to represent skeleton structure of the form

    Details: This skeleton model is used to create the basic structure of a form.
    The internal fields are created using the Field model which reperesents the
    questions of the form.

    Fields:
    - instance: A ForeignKey to the Instance model.
    - title: A CharField for the title of the instance.
    - created_at: A DateTimeField for the creation date of the instance.
    - endMessage: A TextField for the message displayed after the instance ends.
    """
    instance = models.ForeignKey(Instance, related_name='skeletons', on_delete=models.CASCADE, default=None)
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    endMessage = models.TextField(blank=True, null=True)

    def getSkeletonByInstance(instance):
        """
        Get skeleton by instance
        """
        return Skeleton.objects.get(instance=instance)


class Field(models.Model):
    """
    A model to hold all the internal fields of the form

    Details: This model is used to create the internal fields of the form.
    Each field is linked to its parent skeleton and is used to create the
    questions of the form.

    Fields:
    - skeleton: A ForeignKey to the Skeleton model.
    - title: A CharField for the title of the instance.
    - type: A CharField for the type of the instance.
    - required: A BooleanField for the required status of the instance.
    - options: A JSONField for the options of the instance.
    - accepted: A JSONField for the accepted values of the instance.
    """
    skeleton = models.ForeignKey(Skeleton, related_name='fields', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=False, null=False)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, blank=False, null=False)
    required = models.BooleanField(default=False)
    options = models.JSONField(null=True, blank=True)
    accepted = models.JSONField(null=True, blank=True)

    def getFieldById(id):
        """
        Get field by id
        """
        return Field.objects.get(id=id)


class Response(models.Model):
    """
    A model to hold all the responses of the form

    Details: This response model reperesents a particular form submission
    event. It is linked to the skeleton model representing the form structure
    along with submission date.

    Fields:
    - skeleton: A ForeignKey to the Skeleton model.
    - submitted_at: A DateTimeField for the submission date of the instance.
    """
    instance = models.ForeignKey(Instance, related_name='responses', on_delete=models.CASCADE, default=None)
    skeleton = models.ForeignKey(Skeleton, related_name='responses', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(SocialUser,
                             related_name='responses', on_delete=models.CASCADE, null=True, blank=True, default=None)


class Answer(models.Model):
    """
    A model to hold all the answers of the form

    Details: The answer model is used to store the answers of the form.
    Each answer is linked to a field which represents the question. The
    response field is used to link the answer to the response and generate
    a form submission event.

    Fields:
    - response: A ForeignKey to the Response model.
    - field: A ForeignKey to the Field model.
    - value: A TextField for the value of the instance.
    """
    response = models.ForeignKey(Response, related_name='answers', on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    value = models.JSONField(blank=True, null=True)

    def set_value(self, value):
        """
        Set the value of the answer
        """
        if isinstance(value, dict):
            self.value = json.dumps(value)
        else:
            self.value = str(value)

    def get_value(self):
        """
        Get the value of the answer
        """
        try:
            return json.loads(self.value)
        except json.JSONDecodeError:
            return self.value
