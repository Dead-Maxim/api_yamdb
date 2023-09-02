from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

TEXT_LEN = 50


class Reviews(models.Model):
    """Отзыв.
    Атрибуты:
        - author (ForeignKey): Ссылка на модель User, автора записи.
        - text (TextField): Текст отзыва.
        - created (DateTimeField): Дата и время публикации отзыва.
        - title (ForeignKey): Ссылка на модель Title, к которой относится
        отзыв.
    """
    author = models.ForeignKey(
        User,
        verbose_name='Автор отзыва',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField(
        verbose_name='Отзыв',
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews',
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text[:TEXT_LEN]
