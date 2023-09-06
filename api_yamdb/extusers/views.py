from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, pagination, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings

import extusers.serializers as serializers
from extusers.permissions import AdminsHard, AuthUsersHard


User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UsersSerializer
    lookup_field = 'username'
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (AdminsHard,)

    @action(
        detail=False,
        methods=['get', 'patch', ],
        permission_classes=(AuthUsersHard,)
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = serializers.UsersSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            if 'role' in serializer.validated_data:
                serializer.validated_data.pop('role')
            serializer.save()

        serializer = serializers.UsersSerializer(request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers)


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
    serializer_class = serializers.SignupSerializer

    def get_queryset(self):
        return None


class TokenViewSet(PatchAsCreateViewSet):
    permission_classes = [
        permissions.AllowAny,
    ]
    serializer_class = serializers.TokenSerializer

    def get_queryset(self):
        return get_object_or_404(
            User, username=self.kwargs['username'])
