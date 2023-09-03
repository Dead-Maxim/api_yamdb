from django.urls import include, path
from rest_framework.routers import SimpleRouter

from extusers.views import SignupViewSet, TokenViewSet
from api.views import (TitleViewSet, GenreViewSet, CategoryViewSet,
                       ReviewsViewSet)


router = SimpleRouter()
router.register(r'v1/auth/signup', SignupViewSet, basename='signup')
router.register(r'v1/auth/token', TokenViewSet, basename='token')
router.register(r'v1/genres', GenreViewSet, basename="genres")
router.register(r'v1/categories', CategoryViewSet, basename="categories")
router.register(r'v1/titles', TitleViewSet, basename="titles")
router.register(r'v1/reviews', ReviewsViewSet,
                basename="REVIEWS")

urlpatterns = [
    path('', include(router.urls)),
]
