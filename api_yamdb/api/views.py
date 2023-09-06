from rest_framework import viewsets, filters, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from django.db.models import Avg
from rest_framework.response import Response


from api.filters import TitleFilter
from api.serializers import (TitleSerializer,
                             GenreSerializer,
                             CategorySerializer,
                             ReviewSerializer,
                             CommentSerializer)
from reviews.models import Title, Genre, Category, Review, Comment
from extusers.permissions import (Admins,
                                  AuthUsers,
                                  Moderators, SupervisorsHard)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = (Admins,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (Admins,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg("reviews__score"))
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    permission_classes = (Admins,)
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'patch', 'delete']


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Review."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

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


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs['review_id'],
            title__id=self.kwargs['title_id'],
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        return serializer.save(
            author=self.request.user, review=self.get_review()
        )

    def get_permissions(self):
        """Разрешения согласно ТЗ в redoc

        - list (GET): Получение списка всех комментариев.
        Права доступа: Доступно без токена.
        - retrieve (GET): Полуение комментария по id.
        Права доступа: Доступно без токена.
        - create (POST): Добавление нового комментария.
        Права доступа: Аутентифицированные пользователи.
        - partial_update (PATCH): Частичное обновление комментария по id.
        Права доступа: Автор комментария, модератор или администратор.
        - destroy (DELETE): Удаление комментария по id.
        Права доступа: Автор комментария, модератор или администратор.
        - update (PUT): не описан в доке. Не доступен никому
        """
        if self.action in ('list', 'retrieve',):
            return (AllowAny(),)
        elif self.action == 'create':
            return (AuthUsers(),)
        elif self.action in ('partial_update', 'destroy',):
            return (Moderators(),)
        elif self.action == 'update':
            raise MethodNotAllowed(self.request.method)
        else:
            return (SupervisorsHard(),)
