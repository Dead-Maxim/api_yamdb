from django.db.models import Avg
from api.filters import TitleFilter
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend, SearchFilter
from rest_framework import viewsets
from reviews.models import Title, Genre, Category
from extusers.permissions import Admins
from serializers import TitleSerializer, GenreSerializer, CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (Admins,)
    filter_backends = (SearchFilter,)
    search_fields = ("name",)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (Admins,)
    filter_backends = (SearchFilter,)
    search_fields = ("name",)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    )
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (Admins,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
