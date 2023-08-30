from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class MyUser(AbstractUser):
    class Roles(models.TextChoices):
        USER = 'user', _('User')
        MODERATOR = 'moderator', _('Moderator')
        JUNIOR = 'admin', _('Admin')

    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        max_length=16,
        choices=Roles.choices,
        default=Roles.USER,
    )
