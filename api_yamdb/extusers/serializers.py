import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EmailValidator, ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import CurrentUserDefault, ModelSerializer
from rest_framework.validators import UniqueTogetherValidator


User = get_user_model()

class SignupSerializer(ModelSerializer):
    MAX_LEN_USERNAME = 150
    MAX_LEN_EMAIL = 254


    class Meta:
        model = User
        fields = ('username', 'email')
        extra_kwargs = {
            'username': {
                'validators': []
            },
            'email': {
                'validators': []
            },
        }

    def validate_username(self, value):
        if 'me' == value:
            message = _(
                'Использовать это имя в качестве username запрещено.'
            )
            raise serializers.ValidationError(message)

        if len(value) > self.MAX_LEN_USERNAME:
            message = _(
                f'Enter a string with length less or equal {self.MAX_LEN_USERNAME}.'
            )
            raise serializers.ValidationError(message)

        username_validator = UnicodeUsernameValidator()
        try:
            username_validator(value)
        except ValidationError:
            message = _(
                'Enter a valid username. This value may contain only letters, '
                'numbers, and @/./+/-/_ characters.'
            )
            raise serializers.ValidationError(message)
        return value

    def validate_email(self, value):
        if len(value) > self.MAX_LEN_EMAIL:
            message = _(
                f'Enter a string with length less or equal {self.MAX_LEN_EMAIL}.'
            )
            raise serializers.ValidationError(message)

        email_validator = EmailValidator()
        try:
            email_validator(value)
        except ValidationError:
            message = _(
                'Enter a valid email.'
            )
            raise serializers.ValidationError(message)
        return value

    def validate(self, data):
        email = data['email']
        username = data['username']
        users_count = User.objects.filter(
            Q(email=email) | Q(username=username)
        ).count()
        if users_count > 1:
            raise serializers.ValidationError(
                'Плохая комбинация емайла и юзернейма')
        return data

    def create(self, validated_data):
        password = uuid.uuid4().__str__()
        email = validated_data.get('email', None)
        username = validated_data.get('username', None)

        try:
            user = User.objects.get(email=email)
            user.username = username
            user.password = password
            user.save()
        except ObjectDoesNotExist:
            user = User.objects.create(
                email=email, username=username, password=password)

        user.email_user('код подтверждения', password)

        return user


class TokenSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
