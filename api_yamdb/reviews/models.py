from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime

User = get_user_model()

TEXT_LEN = 50
SLUG_LEN = 10
MIN_YEAR = 1
YEAR_NOW = datetime.now().year
TITLE_LEN = 100


class Category(models.Model):
    """Модель Категорий"""

    name = models.CharField(
        max_length=256,
        verbose_name="Название категории",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="поле слаг_Категория",
    )

    def __str__(self):
        return self.slug


class Genre(models.Model):
    """Модель Жанров"""

    name = models.CharField(
        max_length=TEXT_LEN,
        verbose_name="Название жанра",
    )
    slug = models.SlugField(
        max_length=SLUG_LEN,
        unique=True,
        verbose_name="поле слаг_Жанр",
    )

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Модель произведения"""
    name = models.CharField(
        "Наименование произведения", max_length=TITLE_LEN
    )
    year = models.PositiveSmallIntegerField(
        "Год выпуска произведения",
        db_index=True,
        validators=[
            MinValueValidator(MIN_YEAR),
            MaxValueValidator(YEAR_NOW),
        ],
    )
    description = models.TextField(
        "Описание произведения", null=True, blank=True
    )
    genre = models.ManyToManyField(
        "Genre",
        verbose_name="Жанр произведения",
        blank=True,
        related_name="titles",
    )
    category = models.ForeignKey(
        "Category",
        verbose_name="Категория произведения",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="titles",
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
        ordering = ("name",)

    def __str__(self):
        return self.name[:TEXT_LEN]


class GenreTitle(models.Model):
    """Связываем жанр и произведение"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['id']


class Reviews(models.Model):
    """Отзыв.
    Атрибуты:
        - text (TextField): Текст отзыва.
        - author (ForeignKey): Ссылка на модель User, автора записи.
        - pub_date (DateTimeField): Дата и время публикации отзыва.
        - title (ForeignKey): Ссылка на модель Title, к которой относится
        отзыв.
    """
    text = models.TextField(
        verbose_name='Текст отзыва',
    )
    author = models.ForeignKey(
        User,
        verbose_name='username пользователя',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    score = models.IntegerField(
        verbose_name='Оценка от 1 до 10',
        default=1,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации отзыва',
        auto_now_add=True,
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:TEXT_LEN]
