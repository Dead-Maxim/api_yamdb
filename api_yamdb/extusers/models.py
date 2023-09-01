from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        USER = 'user', _('User')
        MODERATOR = 'moderator', _('Moderator')
        ADMIN = 'admin', _('Admin')

    email = models.EmailField(_('email address'),
                              blank=False,
                              unique=True,)

    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        max_length=16,
        choices=Roles.choices,
        default=Roles.USER,
    )
