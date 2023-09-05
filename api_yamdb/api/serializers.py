from django.db.models import Q
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, CurrentUserDefault
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Title, Genre, Category, Review, Comment


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


# class CurrentTitleDefault:
#     requires_context = True
#
#     def __call__(self, serializer_field):
#         return serializer_field.context['request'].data.get('title_id')
#
#     def __repr__(self):
#         return '%s()' % self.__class__.__name__


class ReviewSerializer(ModelSerializer):
    """Сериализатор модели Review."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=CurrentUserDefault()
    )

    title = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=0  # CurrentTitleDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title',)
        read_only_fields = ('author', 'title',)
        extra_kwargs = {'score': {'required': True}}
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('title', 'author')
            )
        ]

    def create(self, validated_data):
        title = validated_data.get('title', None)
        author = validated_data.get('author', None)

        if title is None:
            message = (
                'Не передано значение поля title.'
            )
            raise serializers.ValidationError(message)

        if author is None:
            message = (
                'Не передано значение поля author.'
            )
            raise serializers.ValidationError(message)

        reviews_count = Review.objects.filter(
            Q(title=title) & Q(author=author)
        ).count()
        if reviews_count > 0:
            message = (
                'Уже существуют отзывы автора на это произведение.'
            )
            raise serializers.ValidationError(message)

        review = Review.objects.create(**validated_data)

        return review


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Комментариев"""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author',)
