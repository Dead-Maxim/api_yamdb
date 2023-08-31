from django.contrib.auth import get_user_model
from rest_framework import filters, pagination, permissions, viewsets

from .serializers import SignupSerializer, TokenSerializer


User = get_user_model()


class SignupViewSet(viewsets.ModelViewSet):
    # permission_classes = [
    #     permissions.AllowAny,
    # ]
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def get_queryset(self):
        user = User.objects.get(username=self.request.user.id)
        # user = get_object_or_404(models.User, pk=self.request.user.pk)
        return user.follow_users.all()

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


class TokenViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = TokenSerializer
