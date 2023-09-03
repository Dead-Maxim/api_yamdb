from api.filters import TitleFilter
from rest_framework.pagination import LimitOffsetPagination
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from reviews.models import Title, Genre, Category
from extusers.permissions import Admins
from api.serializers import (TitleSerializer,
                             GenreSerializer,
                             CategorySerializer,
                             ReviewsSerializer)


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


class ReviewsViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Reviews."""
    serializer_class = ReviewsSerializer
    permission_classes = (Admins,)
    pagination_class = LimitOffsetPagination

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.select_related("author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.get_title())
