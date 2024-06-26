from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (CategoryViewSet, CommentViewSet,
                       GenreViewSet, ReviewViewSet, TitleViewSet)
from extusers.views import SignupViewSet, TokenViewSet, UsersViewSet


router = SimpleRouter()
router.register(r'v1/auth/signup', SignupViewSet, basename='signup')
router.register(r'v1/auth/token', TokenViewSet, basename='token')
router.register(r'v1/genres', GenreViewSet, basename="genres")
router.register(r'v1/categories', CategoryViewSet, basename="categories")
router.register(r'v1/titles', TitleViewSet, basename="titles")
router.register(r'v1/titles/(?P<title_id>[^/.]+)/reviews', ReviewViewSet,
                basename="reviews")
router.register(r'v1/users', UsersViewSet, basename="users")
router.register(
    r'v1/titles/(?P<title_id>[^/.]+)/reviews/(?P<review_id>[^/.]+)/comments',
    CommentViewSet, basename="comments")

urlpatterns = [
    path('', include(router.urls)),
]
