from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from reviews.models import Title, Genre, Category


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
