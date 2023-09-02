from django.urls import include, path
from rest_framework.routers import SimpleRouter

from extusers.views import SignupViewSet, TokenViewSet
from api.views import TitleViewSet, GenreViewSet, CategoryViewSet


router = SimpleRouter()
router.register(r'v1/auth/signup', SignupViewSet, basename='signup')
router.register(r'v1/auth/token', TokenViewSet, basename='token')
router.register("genres", GenreViewSet, basename="genres")
router.register("categories", CategoryViewSet, basename="categories")
router.register("titles", TitleViewSet, basename="titles")

urlpatterns = [
    path('', include(router.urls)),
]
