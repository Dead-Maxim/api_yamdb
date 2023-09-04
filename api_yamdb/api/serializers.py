from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, CurrentUserDefault
from reviews.models import Title, Genre, Category, Reviews


class CategoryField(serializers.SlugRelatedField):

    def to_representation(self, value):
        serializer = CategorySerializer(value)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ("id",)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ("id",)


class GenreField(serializers.SlugRelatedField):

    def to_representation(self, value):
        serializer = GenreSerializer(value)
        return serializer.data


class TitleSerializer(ModelSerializer):
    genre = GenreField(
        queryset=Genre.objects.all(),
        slug_field="slug",
        required=False,
        many=True,
    )
    category = CategoryField(
        queryset=Category.objects.all(),
        slug_field="slug",
        required=False,
    )
    rating = serializers.IntegerField(
        required=False
    )

    class Meta:
        model = Title
        fields = "__all__"


class ReviewsSerializer(ModelSerializer):
    """Сериализатор модели Reviews."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=CurrentUserDefault()
    )

    class Meta:
        model = Reviews
        fields = '__all__'
        read_only_fields = ('title',)
        extra_kwargs = {'score': {'required': True}}
