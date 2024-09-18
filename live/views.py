"""
Brief: Django views.py file.

Description: This file contains the views for the Django live app.

Author: Divij Sharma <divijs75@gmail.com>
"""

import jwt
import datetime
import pandas as pd
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from social_core.exceptions import AuthException
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from social_django.utils import load_backend, load_strategy
from core.models import User
from .models import Instance, SocialUser
from .serializers import InstanceSerializer
from .serializers import SocialUserSerializer, SocialUserLoginSerializer
from .serializers import CustomProviderAuthSerializer
from .token import jwt as jwt_custom


USER_SOCIAL_TYPE_OAUTH = 0x1 << 0
USER_SOCIAL_TYPE_USER_LIST = 0x1 << 1


class IsOwner(permissions.BasePermission):
    """
    Custom permission class
    """
    def has_object_permission(self, request, obj):
        """
        Check if the user is the owner of the instance object.
        """
        return obj.user == request.user


class InstanceListCreateView(generics.ListCreateAPIView):
    """
    List and create view for the Instance object.
    """
    serializer_class = InstanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filters the instances for the current user.
        """
        return Instance.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Save the instance object with the user field set to the current user.
        """
        serializer.save(user=self.request.user)


class InstanceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update and destroy view for the Instance object.
    """
    serializer_class = InstanceSerializer
    lookup_field = 'hash'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filters the instances for the current user.
        """
        return Instance.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        """
        If the user is the owner of the instance object, save the instance object.
        """
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this instance.")
        serializer.save(last_modified=datetime.datetime.now())

    def perform_destroy(self, instance):
        """
        If the user is the owner of the instance object, delete the instance object.
        """
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this instance.")
        instance.delete()


class InstanceTypeStatusView(APIView):
    """
    Get the type and status of all instances without authentication.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST request to fetch type and status of all instances.
        """
        hash_value = request.data.get('hash')
        if not hash_value:
            return Response({"detail": "Hash is required."}, status=400)

        try:
            instance = Instance.objects.get(hash=hash_value)
        except Instance.DoesNotExist:
            raise NotFound("Instance with the provided hash does not exist.")

        data = {
            'hash': instance.hash,
            'instance_auth_type': instance.instance_auth_type,
            'instance_status': instance.instance_status,
        }
        return Response(data)


class InstanceCSVView(APIView):
    """
    View handle CSV file uploads and downloads for the SocialUser object.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request, hash, *args, **kwargs):
        """
        Handle POST request to add users from a CSV file.
        """
        try:
            instance = Instance.getInstance(hash, request.user)
        except Instance.DoesNotExist:
            return Response({"detail": "Instance with the provided hash does not exist."},
                            status=404)
        if 'file' not in request.FILES:
            return Response({"detail": "File is required."}, status=400)
        csv_file = request.FILES.get('file')
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            return Response({"detail": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        for index, row in df.iterrows():
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            username = request.data.get('username')
            password = request.data.get('password')

            if not username or not password:
                return Response({"detail": "Username and password fields are required."},
                                status=400)

            if username not in df.columns or password not in df.columns:
                return Response({"detail": "Username and password fields are required in the CSV"},
                                status=status.HTTP_400_BAD_REQUEST)
            if row[username] == '' or row[password] == '':
                return Response({"detail": "Username and password fields cannot be empty."},
                                status=400)
            try:
                SocialUser.objects.create(
                    instance=instance,
                    user_social_type=0x1 << 1,
                    first_name=row[first_name] if not pd.isnull(row[first_name]) else '',
                    last_name=row[last_name] if not pd.isnull(row[last_name]) else '',
                    username=row[username],
                    password=make_password(row[password]),
                )
            except Exception as e:
                return Response({"detail": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Users added successfully"}, status=status.HTTP_201_CREATED)

    def get(self, request, hash, username=None, *args, **kwargs):
        """
        Handle GET request to get all users or a single user by username or download the users as a CSV file.
        """
        try:
            instance = Instance.getInstance(hash, request.user)
        except Instance.DoesNotExist:
            return Response({"detail": "Instance with the provided hash does not exist."},
                            status=404)
        if 'download' in request.path:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="users.csv"'
            users = SocialUser.objects.filter(
                instance=instance, user_social_type=USER_SOCIAL_TYPE_USER_LIST)
            serializer = SocialUserSerializer(users, many=True)
            df = pd.DataFrame(serializer.data)
            df.to_csv(path_or_buf=response, index=False)
            return response

        if username:
            user = get_object_or_404(
                SocialUser, instance=instance, username=username,
                user_social_type=USER_SOCIAL_TYPE_USER_LIST)
            serializer = SocialUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        users = SocialUser.objects.filter(
            instance=instance, user_social_type=USER_SOCIAL_TYPE_USER_LIST)
        serializer = SocialUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, hash, username, *args, **kwargs):
        """
        Handle PATCH request to update a user by username.
        """
        try:
            instance = Instance.getInstance(hash, request.user)
        except Instance.DoesNotExist:
            return Response({"detail": "Instance with the provided hash does not exist."},
                            status=404)
        user = get_object_or_404(
            SocialUser, instance=instance, username=username,
            user_social_type=USER_SOCIAL_TYPE_USER_LIST)
        serializer = SocialUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, hash, username, *args, **kwargs):
        """
        Handle DELETE request to delete a user by username.
        """
        try:
            instance = Instance.getInstance(hash, request.user)
        except Instance.DoesNotExist:
            return Response({"detail": "Instance with the provided hash does not exist."},
                            status=404)
        user = get_object_or_404(
            SocialUser, instance=instance, username=username,
            user_social_type=USER_SOCIAL_TYPE_USER_LIST)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InstanceJSONView(APIView):
    """
    View handle JSON file uploads and downloads for the SocialUser object.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request, hash, *args, **kwargs):
        """
        Handle POST request to add users from a JSON file.
        """
        try:
            instance = Instance.getInstance(hash, request.user)
        except Instance.DoesNotExist:
            return Response({"detail": "Instance with the provided hash does not exist."},
                            status=404)
        json_file = request.FILES.get('file')
        try:
            df = pd.read_json(json_file)
        except Exception as e:
            return Response({"detail": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        for index, row in df.iterrows():
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            username = request.data.get('username')
            password = request.data.get('password')

            if not username or not password:
                return Response({"detail": "Username and password fields are required."},
                                status=400)

            if username not in df.columns or password not in df.columns:
                return Response({"detail": "Username and password fields are required in JSON"},
                                status=status.HTTP_400_BAD_REQUEST)
            if row[username] == '' or row[password] == '':
                return Response({"detail": "Username and password fields cannot be empty."},
                                status=400)

            try:
                SocialUser.objects.create(
                    instance=instance,
                    user_social_type=0x1 << 1,
                    first_name=row[first_name] if not pd.isnull(row[first_name]) else '',
                    last_name=row[last_name] if not pd.isnull(row[last_name]) else '',
                    username=row[username],
                    password=make_password(row[password]),
                )
            except Exception as e:
                return Response({"detail": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Users added successfully"}, status=status.HTTP_201_CREATED)

    def get(self, request, hash, username=None, *args, **kwargs):
        """
        Handle GET request to get all users or a single user by username or download the users as a JSON file.
        """
        try:
            instance = Instance.getInstance(hash, request.user)
        except Instance.DoesNotExist:
            return Response({"detail": "Instance with the provided hash does not exist."},
                            status=404)
        if 'download' in request.path:
            response = HttpResponse(content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="users.json"'
            users = SocialUser.objects.filter(
                instance=instance, user_social_type=USER_SOCIAL_TYPE_USER_LIST)
            serializer = SocialUserSerializer(users, many=True)
            response.write(serializer.data)
            return response
        if username:
            user = get_object_or_404(
                SocialUser, instance=instance, username=username,
                user_social_type=USER_SOCIAL_TYPE_USER_LIST)
            serializer = SocialUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        users = SocialUser.objects.filter(
            instance=instance, user_social_type=USER_SOCIAL_TYPE_USER_LIST)
        serializer = SocialUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, hash, username, *args, **kwargs):
        """
        Handle PATCH request to update a user by username.
        """
        try:
            instance = Instance.getInstance(hash, request.user)
        except Instance.DoesNotExist:
            return Response({"detail": "Instance with the provided hash does not exist."},
                            status=404)
        user = get_object_or_404(
            SocialUser, instance=instance, username=username,
            user_social_type=USER_SOCIAL_TYPE_USER_LIST)
        serializer = SocialUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, hash, username, *args, **kwargs):
        """
        Handle DELETE request to delete a user by username.
        """
        try:
            instance = Instance.getInstance(hash, request.user)
        except Instance.DoesNotExist:
            return Response({"detail": "Instance with the provided hash does not exist."},
                            status=404)
        user = get_object_or_404(
            SocialUser, instance=instance, username=username,
            user_social_type=USER_SOCIAL_TYPE_USER_LIST)
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class InstanceOrganizationView(APIView):
    """
    View to get the Social Users within an organization.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, hash, username=None, *args, **kwargs):
        """
        Handle GET request to get all users or a single user by username or download the users in specified format.
        """
        try:
            instance = Instance.getInstance(hash, request.user)
        except Instance.DoesNotExist:
            return Response({"detail": "Instance with the provided hash does not exist."},
                            status=404)
        if 'download' in request.path:

            if 'format' not in request.query_params:
                return Response({"detail": "Format is required for download."}, status=400)

            users = SocialUser.objects.filter(
                instance=instance, user_social_type=USER_SOCIAL_TYPE_OAUTH)
            serializer = SocialUserSerializer(users, many=True)

            if request.query_params['format'] == 'json':
                response = HttpResponse(content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename="users.json"'
                response.write(serializer.data)
                return response
            elif request.query_params['format'] == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="users.csv"'
                df = pd.DataFrame(serializer.data)
                df.to_csv(path_or_buf=response, index=False)
                return response
            else:
                return Response({"detail": "Invalid format for download."}, status=400)

        if username:
            user = get_object_or_404(
                SocialUser, instance=instance, username=username,
                user_social_type=USER_SOCIAL_TYPE_OAUTH)
            serializer = SocialUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        users = SocialUser.objects.filter(
            instance=instance, user_social_type=USER_SOCIAL_TYPE_OAUTH)
        serializer = SocialUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SocialUserTokenObtainPairView(APIView):
    """
    View to obtain the token pair for the SocialUser object.
    """
    permission_classes = [AllowAny]

    def post(self, request, hash, *args, **kwargs):
        """
        Handle POST request to obtain the token pair for the SocialUser object.
        """
        serializer = SocialUserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        try:
            instance = Instance.getExistingInstance(hash)
        except Instance.DoesNotExist:
            return Response({"detail": "Instance with the provided hash does not exist."},
                            status=404)
        try:
            social_user = SocialUser.objects.get(username=username, instance=instance)
        except SocialUser.DoesNotExist:
            return Response({"detail": "Invalid credentials"},
                            status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, social_user.password):
            return Response({"detail": "Invalid credentials"},
                            status=status.HTTP_401_UNAUTHORIZED)

        payload = {
            'social_user_id': social_user.id,
            'username': social_user.username,
            'exp': datetime.datetime.now() + datetime.timedelta(days=1)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return Response({'access': token}, status=status.HTTP_201_CREATED)


class ProviderAuthView(generics.CreateAPIView):
    """
    View to authenticate a user with a custom provider.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomProviderAuthSerializer

    def get(self, request, *args, **kwargs):
        """
        Override GET request to authenticate a user with a custom provider.
        """
        redirect_uri = request.GET.get("redirect_uri")
        instance_hash = self.kwargs["hash"]
        if redirect_uri not in settings.SOCIAL_AUTH_ALLOWED_REDIRECT_URIS:
            return Response(
                data={"detail": "Invalid redirect URI"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        strategy = load_strategy(request)
        strategy.session_set("redirect_uri", redirect_uri)
        cache.set("redirect_uri", redirect_uri, timeout=60)
        cache.set("instance_hash", instance_hash, timeout=60)

        backend_name = self.kwargs["provider"]
        backend = load_backend(strategy, backend_name, redirect_uri=redirect_uri)

        authorization_url = backend.auth_url()
        state = backend.get_session_state()
        cache.set("google-oauth2_state", state, timeout=60)
        strategy.session_set("google-oauth2_state", state)
        return Response(data={"authorization_url": authorization_url})

    def perform_create(self, serializer):
        """
        Handle post create operations.
        """
        instance = serializer.save()
        social_user_username = instance.get('user')
        try:
            user_obj = User.objects.get(email=social_user_username)
            user_obj.delete()
        except User.DoesNotExist:
            pass

    def get_serializer_context(self):
        """
        Add instance hash to the serializer context.
        """
        context = super().get_serializer_context()
        context['hash'] = self.kwargs['hash']
        return context


class GoogleOAuthCallbackView(APIView):
    """
    View to handle the callback from Google OAuth2 and exchange the authorization code for an access token.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        state = request.GET.get("state")
        hash = cache.get("instance_hash")

        instance = Instance.getExistingInstance(hash)

        if not code or not state:
            return Response({"details": "Missing code or state in the request"}, status=status.HTTP_400_BAD_REQUEST)

        strategy = load_strategy(request)
        redirect_uri = cache.get("redirect_uri")
        backend = load_backend(strategy=strategy, name='google-oauth2', redirect_uri=redirect_uri)
        strategy.session_set("google-oauth2_state", cache.get("google-oauth2_state"))

        try:
            user = backend.auth_complete()
            allowed_domains = instance.allowed_domains
            if allowed_domains != ["*"] and user.email.split("@")[1] not in allowed_domains:
                try:
                    user_obj = User.objects.get(email=user.email)
                    user_obj.delete()
                except User.DoesNotExist:
                    pass
                frontend_permissiondenied_url = settings.FRONTEND_REDIRECT_URL_NOTALLOWED
                return redirect(frontend_permissiondenied_url)

            social_user = self.get_or_create_social_user(user, hash)
            token = jwt_custom.TokenStrategy.obtain(social_user)

        except AuthException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        frontend_url = settings.FRONTEND_REDIRECT_URL + f"?access={token['access']}"
        return redirect(frontend_url)

    def get_or_create_social_user(self, user, hash):
        """
        Create a social user if it doesn't exist or return the existing one.
        """
        instance = Instance.getExistingInstance(hash)

        try:
            social_user = SocialUser.objects.get(username=user.email, instance=instance)
        except SocialUser.DoesNotExist:
            social_user = SocialUser.objects.create(
                instance=instance,
                user_social_type=0x1 << 0,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.email,
                password=make_password(user.password)
            )

        try:
            user_obj = User.objects.get(email=user.email)
            user_obj.delete()
        except User.DoesNotExist:
            pass

        return social_user
