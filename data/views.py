"""
Brief: Django views.py file.

Description: This file contains the views for the Django data app.

Author: Divij Sharma <divijs75@gmail.com>
"""

import jwt
from rest_framework import generics
from .models import Skeleton, Field, Answer, Response
from live.models import Instance, SocialUser
from .serializers import SkeletonSerializer, FieldSerializer, AnswerSerializer, ResponseSerializer
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction


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


class ResponseListCreateView(generics.ListAPIView):
    """
    View to list rhe responses for the form.
    """

    serializer_class = ResponseSerializer

    def get_queryset(self):
        """
        Get the responses for the given form
        """
        hash = self.kwargs.get('hash')
        user = self.request.user
        instance = check_form_accessible(user, hash)
        return Response.objects.filter(instance=instance)


class ResponseDetailView(generics.RetrieveDestroyAPIView):
    """
    View to retrieve and delete Responses.
    """
    serializer_class = ResponseSerializer

    def get_object(self):
        """
        Get the response for the given form
        """
        hash = self.kwargs.get('hash')
        user = self.request.user
        check_form_accessible(user, hash)
        response_pk = self.kwargs.get('pk')
        try:
            return Response.objects.get(pk=response_pk)
        except Response.DoesNotExist:
            raise NotFound(detail="No response matches the given query.")


def check_form_accessible(user, hash):
    """
    Check if the form is accessible by the user
    """
    try:
        instance = Instance.objects.get(hash=hash, user=user)
    except Instance.DoesNotExist:
        raise NotFound(detail="No instance matches the given query.")
    return instance


@api_view(['GET'])
@permission_classes([AllowAny])
def custom_get_method(request, hash, *args, **kwargs):
    """
    Custom GET method for the form when accessing the form as a voter.
    """
    try:
        instance = Instance.getExistingInstance(hash)
    except Instance.DoesNotExist:
        return JsonResponse({"detail": "Instance not found"}, status=404)

    if instance.instance_status == 0x1 << 0:
        return JsonResponse({"detail": "Instance is no longer accepting responses"}, status=403)

    auth_type = instance.instance_auth_type

    token = None
    if 'access' in request.GET:
        token = request.GET.get('access')

    if auth_type == 0x1 << 0:
        # Public access, no token required
        skeletons = Skeleton.objects.filter(instance=instance)
        serializer = SkeletonSerializer(skeletons, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)

    if auth_type in [0x1 << 1, 0x1 << 2]:
        # Either social user or listed user access, token required
        if not token:
            return JsonResponse({"detail": "Access token is required"}, status=403)

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            social_user_id = decoded_token.get('social_user_id')
            user = SocialUser.objects.filter(id=social_user_id).first()
            if not user:
                return JsonResponse({"detail": "Invalid access token"}, status=403)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"detail": "Token has expired"}, status=403)
        except jwt.InvalidTokenError:
            return JsonResponse({"detail": "Invalid access token"}, status=403)

        request.user = user
        skeletons = Skeleton.objects.filter(instance=instance)
        serializer = SkeletonSerializer(skeletons, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)

    return JsonResponse({"detail": "Unauthorized"}, status=403)


@api_view(['POST'])
@permission_classes([AllowAny])
def custom_post_method(request, hash, *args, **kwargs):
    """
    Custom POST method for the form when submitting the form as a voter.
    """
    try:
        instance = Instance.getExistingInstance(hash)
    except Instance.DoesNotExist:
        return JsonResponse({"detail": "Instance not found"}, status=404)

    if instance.instance_status == 0x1 << 0:
        return JsonResponse({"detail": "Instance is no longer accepting responses"}, status=403)

    auth_type = instance.instance_auth_type

    token = None
    if 'access' in request.GET:
        token = request.GET.get('access')

    data = request.data.get('answers', [])
    if not data:
        return JsonResponse({"detail": "Answers are required"}, status=400)
    if auth_type == 0x1 << 0:
        # Public access, no token required
        required_fields = Field.objects.filter(
            skeleton=Skeleton.getSkeletonByInstance(instance=instance), required=True)
        required_fields_ids = [field.id for field in required_fields]
        for id in data:
            if int(id["id"]) not in required_fields_ids:
                return JsonResponse({"detail": "Required fields are missing"}, status=400)

        response = populate_answers_and_responses(data=data, instance=instance)
        return JsonResponse(response, safe=False, status=201)

    if auth_type in [0x1 << 1, 0x1 << 2]:
        # Either social user or listed user access, token required
        if not token:
            return JsonResponse({"detail": "Access token is required"}, status=403)

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            social_user_id = decoded_token.get('social_user_id')
            user = SocialUser.objects.filter(id=social_user_id).first()
            if user.has_voted:
                return JsonResponse({"detail": "You have already voted"}, status=403)
            user.has_voted = True
            user.save()
            if not user:
                return JsonResponse({"detail": "Invalid access token"}, status=403)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"detail": "Token has expired"}, status=403)
        except jwt.InvalidTokenError:
            return JsonResponse({"detail": "Invalid access token"}, status=403)

        request.user = user
        required_fields = Field.objects.filter(
            skeleton=Skeleton.getSkeletonByInstance(instance=instance), required=True)
        required_fields_ids = [field.id for field in required_fields]
        for id in data:
            if int(id["id"]) not in required_fields_ids:
                return JsonResponse({"detail": "Required fields are missing"}, status=400)

        response = populate_answers_and_responses(data=data, user=user, instance=instance)
        return JsonResponse(response, safe=False, status=201)

    return JsonResponse({"detail": "Unauthorized"}, status=403)


def populate_answers_and_responses(data, instance, user=None):
    """
    Populate the answers and responses for the form
    """
    if not isinstance(data, list):
        raise ValueError("Invalid data format for answers, list expected.")
    skeleton = Skeleton.getSkeletonByInstance(instance=instance)
    response = Response.objects.create(instance=instance, skeleton=skeleton, user=user)

    atomic_trans_actions = []

    for answer_data in data:
        try:
            answer_data['field'] = answer_data.pop('id')
        except Exception:
            response.delete()
            raise NotFound("Id and value are required for answer")
        serializer = AnswerSerializer(data=answer_data)
        if serializer.is_valid():
            field = serializer.validated_data.get('field')
            value = serializer.validated_data.get('value')
            answer = Answer(
                response=response,
                field=field,
                value=value
            )
            atomic_trans_actions.append(answer)
        else:
            response.delete()
            raise NotFound(f"Invalid data for answer: {serializer.errors}")

    try:
        with transaction.atomic():
            Answer.objects.bulk_create(atomic_trans_actions)
    except Exception as e:
        response.delete()
        raise e
    return_respnse = ResponseSerializer(response).data
    return return_respnse
