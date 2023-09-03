import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EmailValidator, ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class UsersSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email',
            'first_name', 'last_name', 'bio',
            'role',
        )


class MeSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email',
            'first_name', 'last_name', 'bio',
            'role',
        )
        extra_kwargs = {
            'role': {
                'read_only': True,
            },
        }

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.bio = validated_data.get('bio', instance.bio)

        instance.save()
        return instance


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
                f'Enter a string with length '
                f'less or equal {self.MAX_LEN_USERNAME}.'
            )
            raise serializers.ValidationError(message)

        username_validator = UnicodeUsernameValidator()
        try:
            username_validator(value)
        except ValidationError:
            message = _(
                'Enter a valid username. '
                'This value may contain only letters, '
                'numbers, and @/./+/-/_ characters.'
            )
            raise serializers.ValidationError(message)
        return value

    def validate_email(self, value):
        if len(value) > self.MAX_LEN_EMAIL:
            message = _(
                f'Enter a string with length '
                f'less or equal {self.MAX_LEN_EMAIL}.'
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


class ConfirmationCodeField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data


class TokenSerializer(ModelSerializer):
    confirmation_code = ConfirmationCodeField(
        source="password", write_only=True)
    token = serializers.SerializerMethodField('get_token')

    class Meta:
        model = User
        fields = ('username', 'confirmation_code', 'token',)
        extra_kwargs = {
            'confirmation_code': {
                'write_only': True,
                'validators': [],
            },
            'username': {
                'write_only': True,
                'validators': [],
            },
        }

    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)

        return str(refresh.access_token)

    def validate(self, data):
        username = data['username']
        confirmation_code = data['password']
        user = get_object_or_404(User, username=username)

        # valid_password = user.check_password(confirmation_code)
        valid_password = confirmation_code == user.password
        if not valid_password:
            message = 'invalid confirmation code value; check latest email'
            raise serializers.ValidationError(message)

        return data

    def create(self, validated_data):
        return User.objects.get(username=validated_data.get('username'))
