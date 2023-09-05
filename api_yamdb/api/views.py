from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import (
    LimitOffsetPagination, PageNumberPagination)
from rest_framework.permissions import AllowAny

from api.filters import TitleFilter
from api.serializers import (TitleSerializer,
                             GenreSerializer,
                             CategorySerializer,
                             ReviewSerializer)
from reviews.models import Title, Genre, Category, Review
from extusers.permissions import (Admins,
                                  AuthUsers,
                                  Moderators)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (Admins,)
    filter_backends = (filters.DjangoFilterBackend,)
    search_fields = ("name",)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (Admins,)
    filter_backends = (filters.DjangoFilterBackend,)
    search_fields = ("name",)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (Admins,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TitleFilter


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Review."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete',]

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.select_related("author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def get_permissions(self):
        """Разрешения согласно ТЗ в redoc

        - list (GET): Получение списка всех отзывов.
        Права доступа: Доступно без токена.
        - retrieve (GET): Полуение отзыва по id.
        Права доступа: Доступно без токена.
        - create (POST): Добавление нового отзыва.
        Права доступа: Аутентифицированные пользователи.
        - partial_update (PATCH): Частичное обновление отзыва по id.
        Права доступа: Автор отзыва, модератор или администратор.
        - destroy (DELETE): Удаление отзыва по id.
        Права доступа: Автор отзыва, модератор или администратор.
        - update (PUT): не описан в доке. Не доступен никому
        """
        if self.action in ('list', 'retrieve',):
            return (AllowAny(),)
        elif self.action == 'create':
            return (AuthUsers(),)
        elif self.action in ('partial_update', 'destroy',):
            return (Moderators(),)
        else:
            raise MethodNotAllowed(self.request.method)
