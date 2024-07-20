"""
Brief: Django serializers.py file.

Description: This file contains the serializers for the Django data app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from rest_framework import serializers
from .models import Skeleton, Field, Response, Answer

class FieldSerializer(serializers.ModelSerializer):
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
                raise serializers.ValidationError({'options': 'Options are required when adding choice based questions.'})
        else:
            if options is not None:
                # Optionally: Add additional validation if needed
                pass

        # Validate 'accepted' field based on 'type'
        if field_type == 'file':
            if accepted is None:
                raise serializers.ValidationError({'accepted': 'Allowed file types are required when adding file upload questions.'})
        else:
            if accepted is not None:
                # Optionally: Add additional validation if needed
                pass

        return data


class SkeletonSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True)

    class Meta:
        model = Skeleton
        fields = ['id', 'title', 'created_at', 'endMessage', 'fields']
    
    def create(self, validated_data):
        fields_data = validated_data.pop('fields', [])
        skeleton = Skeleton.objects.create(**validated_data)
        for field_data in fields_data:
            Field.objects.create(skeleton=skeleton, **field_data)
        return skeleton

    def update(self, instance, validated_data):
        fields_data = validated_data.pop('fields', [])
        # Update instance fields
        instance.title = validated_data.get('title', instance.title)
        instance.endMessage = validated_data.get('endMessage', instance.endMessage)
        instance.save()
        return instance

class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ['id', 'skeleton', 'submitted_at']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'response', 'field', 'value']
