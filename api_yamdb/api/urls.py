from django.urls import include, path
from rest_framework.routers import SimpleRouter

from extusers.views import SignupViewSet, TokenViewSet


router = SimpleRouter()
router.register(r'v1/auth/signup', SignupViewSet, basename='signup')
router.register(r'v1/auth/token', TokenViewSet, basename='token')

urlpatterns = [
    path('', include(router.urls)),
]
