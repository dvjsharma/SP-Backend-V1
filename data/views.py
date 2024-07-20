"""
Brief: Django views.py file.

Description: This file contains the views for the Django data app.

Author: Divij Sharma <divijs75@gmail.com>
"""

from rest_framework import generics
from .models import Skeleton, Field, Answer
from live.models import Instance
from .serializers import SkeletonSerializer, FieldSerializer, AnswerSerializer
from rest_framework.exceptions import NotFound, ValidationError


class FormListCreateView(generics.ListCreateAPIView):
    """
    View to list and create forms.
    """
    serializer_class = SkeletonSerializer

    def get_queryset(self):
        """
        Get the forms for the given instance.
        """
        hash = self.kwargs.get('hash')
        user = self.request.user
        instance = check_form_accessible(user, hash)
        return Skeleton.objects.filter(instance=instance)

    def perform_create(self, serializer):
        """
        Create a new form for the given
        """
        instance_hash = self.kwargs.get('hash')
        try:
            instance = Instance.getInstance(hash=instance_hash, user=self.request.user)
        except Instance.DoesNotExist:
            raise NotFound(detail="No instance found for the given hash")
        try:
            Skeleton.objects.get(instance=instance)
            raise ValidationError(
                {"detail": "Form already exists for the given instance, use the update endpoint instead."})
        except Skeleton.DoesNotExist:
            serializer.save(instance=instance)


class FormDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update and delete forms.
    """
    serializer_class = SkeletonSerializer

    def get_queryset(self):
        """
        Get the form for the given instance
        """
        hash = self.kwargs.get('hash')
        user = self.request.user
        instance = check_form_accessible(user, hash)
        return Skeleton.objects.filter(instance=instance)


class QuestionListCreateView(generics.ListCreateAPIView):
    """
    View to list and create questions.
    """
    serializer_class = FieldSerializer

    def get_queryset(self):
        """
        Get the questions for the given form
        """
        hash = self.kwargs.get('hash')
        user = self.request.user
        check_form_accessible(user, hash)
        form_pk = self.kwargs.get('pk')
        return Field.objects.filter(skeleton_id=form_pk)

    def perform_create(self, serializer):
        """
        Create a new question for the given form
        """
        hash = self.kwargs.get('hash')
        user = self.request.user
        check_form_accessible(user, hash)
        form_pk = self.kwargs.get('pk')
        try:
            skeleton = Skeleton.objects.get(pk=form_pk)
        except Skeleton.DoesNotExist:
            raise NotFound(detail="No Skeleton matches the given query.")
        serializer.save(skeleton=skeleton)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update and delete questions.
    """
    serializer_class = FieldSerializer

    def get_object(self):
        """
        Get the question for the given form
        """
        hash = self.kwargs.get('hash')
        user = self.request.user
        check_form_accessible(user, hash)
        form_pk = self.kwargs.get('pk')
        item_pk = self.kwargs.get('itempk')
        try:
            return Field.objects.get(skeleton_id=form_pk, id=item_pk)
        except Field.DoesNotExist:
            raise NotFound(detail="No question matches the given query.")


class AnswerListCreateView(generics.ListCreateAPIView):
    """
    View to list and create answers.
    """
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def get_queryset(self):
        """
        Get the answers for the given response
        """
        response_id = self.request.query_params.get('response_id')
        if response_id:
            return Answer.objects.filter(response_id=response_id)
        return Answer.objects.all()


class AnswerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update and delete answers.
    """
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer


def check_form_accessible(user, hash):
    """
    Check if the form is accessible by the user
    """
    try:
        instance = Instance.objects.get(hash=hash, user=user)
    except Instance.DoesNotExist:
        raise NotFound(detail="No instance matches the given query.")
    return instance
