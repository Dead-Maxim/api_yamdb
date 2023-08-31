from django.urls import include, path
from rest_framework.routers import SimpleRouter

from extusers.views import SignupViewSet, TokenViewSet


router = SimpleRouter()
router.register(r'v1/auth/signup', SignupViewSet)
router.register(r'v1/auth/token', TokenViewSet)

urlpatterns = [
    # path('v1/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]
