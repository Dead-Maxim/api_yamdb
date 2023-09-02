from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.settings import api_settings

from .serializers import SignupSerializer, TokenSerializer


User = get_user_model()


class PatchAsCreateViewSet(viewsets.GenericViewSet):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class SignupViewSet(PatchAsCreateViewSet):
    permission_classes = [
        permissions.AllowAny,
    ]
    serializer_class = SignupSerializer

    def get_queryset(self):
        return None


class TokenViewSet(PatchAsCreateViewSet):
    permission_classes = [
        permissions.AllowAny,
    ]
    serializer_class = TokenSerializer

    def get_queryset(self):
        return get_object_or_404(
            User, username=self.kwargs['username'])
