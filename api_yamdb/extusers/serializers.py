from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import CurrentUserDefault, ModelSerializer
from rest_framework.validators import UniqueTogetherValidator


User = get_user_model()

class SignupSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class TokenSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
