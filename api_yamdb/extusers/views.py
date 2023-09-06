from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import (
    filters, pagination, permissions, status, viewsets)
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
        methods=['get', 'patch',],
        permission_classes=(AuthUsersHard,)
    )
    def me(self, request):
        # if not request.user.is_authenticated:
        #     pass

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

    # def get_permissions(self):
    #     """Разрешения согласно ТЗ в redoc
#
    #     - list (GET): Получить список всех пользователей.
    #     Права доступа: Администратор.
    #     - retrieve (GET): Получить пользователя по username.
    #     Права доступа: Администратор.
    #     - create (POST): Добавить нового пользователя.
    #     Права доступа: Администратор.
    #     - partial_update (PATCH): Изменить данные пользователя по username.
    #     Права доступа: Администратор.
    #     - destroy (DELETE): Удалить пользователя по username.
    #     Права доступа: Администратор.
    #     - update (PUT): не описан в доке. Не доступен никому
    #     """
        # if self.action in (
        #         'list', 'retrieve',
        #         'create' 'partial_update',
        #         'destroy',
        # ):
        #     return (AdminsHard(),)
        # else:
        #     raise MethodNotAllowed(self.request.method)
        # return (AdminsHard(),)


# class MeViewSet(
#     mixins.RetrieveModelMixin,
#     mixins.UpdateModelMixin,
#     viewsets.GenericViewSet
# ):
#     queryset = User.objects.all()
#     permission_classes = [
#         AuthUsers,
#     ]
#     serializer_class = serializers.MeSerializer
#     http_method_names = ['get', 'patch',]
#
#     def get_queryset(self):
#         return get_object_or_404(User, pk=self.request.user.pk)
#
#     def get_object(self):
#         return get_object_or_404(User, pk=self.request.user.pk)


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
