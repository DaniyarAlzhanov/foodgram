from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from api.validators import validate_username
from foodgram.settings import (
    MAX_LENGTH_OF_EMAIL,
    MAX_LENGTH_OF_USERNAME,
    MAX_LENGTH_OF_FIRST_NAME,
    MAX_LENGTH_OF_LAST_NAME,
    MESSAGE_FOR_USERNAME_VALIDATOR,
)


class User(AbstractUser):
    """Кастомная модель пользователей."""

    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=MAX_LENGTH_OF_EMAIL,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Никнейм пользователя',
        max_length=MAX_LENGTH_OF_USERNAME,
        validators=[
            UnicodeUsernameValidator(
                message=MESSAGE_FOR_USERNAME_VALIDATOR
            ),
            validate_username,
        ],
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=MAX_LENGTH_OF_FIRST_NAME,
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=MAX_LENGTH_OF_LAST_NAME,
    )
    avatar = models.ImageField(
        verbose_name='Аватар пользователя',
        upload_to='users/images/',
        default=None,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = (
            'username',
            'email',
        )

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
        )

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}.'
