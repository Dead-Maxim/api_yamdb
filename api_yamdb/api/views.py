from django.db.models import Avg
from api.filters import TitleFilter
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from reviews.models import Title
from extusers.permissions import Admins


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    )
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (Admins,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
