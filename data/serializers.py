"""
Brief: Django serializers.py file.

Description: This file contains the serializers for the Django data app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from rest_framework import serializers
from .models import Skeleton, Field, Response, Answer


class FieldSerializer(serializers.ModelSerializer):
    """
    Field Serializer for the Field model.
    """
    options = serializers.JSONField(required=False, allow_null=True)
    accepted = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = Field
        fields = ['id', 'title', 'type', 'required', 'options', 'accepted']

    def validate(self, data):
        """
        Check that the required fields are present based on the type of field.
        """
        field_type = data.get('type')
        options = data.get('options')
        accepted = data.get('accepted')

        # Validate 'options' field based on 'type'
        if field_type in ['multioption-singleanswer', 'multioption-multianswer']:
            if options is None:
                raise serializers.ValidationError(
                    {'options': 'Options are required when adding choice based questions.'})
        else:
            if options is not None:
                pass

        if field_type == 'file':
            if accepted is None:
                raise serializers.ValidationError(
                    {'accepted': 'Allowed file types are required when adding file upload questions.'})
        else:
            if accepted is not None:
                pass
        return data


class SkeletonSerializer(serializers.ModelSerializer):
    """
    Skeleton Serializer for the Skeleton model.
    """
    fields = FieldSerializer(many=True)

    class Meta:
        model = Skeleton
        fields = ['id', 'title', 'description', 'created_at', 'fields', 'endMessage']

    def create(self, validated_data):
        """
        Create the Skeleton object along with the fields.
        """
        fields_data = validated_data.pop('fields', [])
        skeleton = Skeleton.objects.create(**validated_data)
        for field_data in fields_data:
            Field.objects.create(skeleton=skeleton, **field_data)
        return skeleton

    def update(self, instance, validated_data):
        """
        Update the Skeleton object along with the fields.
        """
        validated_data.pop('fields', [])
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.endMessage = validated_data.get('endMessage', instance.endMessage)
        instance.save()
        return instance


class AnswerSerializer(serializers.ModelSerializer):
    """
    Answer Serializer for the Answer model.
    """
    field = serializers.PrimaryKeyRelatedField(queryset=Field.objects.all())

    class Meta:
        model = Answer
        fields = ['field', 'value']


class ResponseSerializer(serializers.ModelSerializer):
    """
    Response Serializer for the Response model.
    """
    answers = AnswerSerializer(many=True)
    user = serializers.SerializerMethodField()

    class Meta:
        model = Response
        fields = ['id', 'submitted_at', 'user', 'answers']

    def get_user(self, obj):
        """
        Return the username of the user who created the response.
        """
        return obj.user.username if obj.user else None
