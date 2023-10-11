from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from basys import texts
from basys.validators import validate_name


class CustomUser(AbstractUser):
    """Пользователь"""
    username = models.CharField(
        max_length=settings.MAX_LEN_USERS_FIELD,
        unique=True,
        validators=[validate_name],
        help_text=texts.HELP_USERNAME,
    )

    first_name = models.CharField(
        max_length=settings.MAX_LEN_USERS_FIELD,
        verbose_name='Имя',
        help_text=texts.HELP_FIRST_NAME,
    )

    last_name = models.CharField(
        max_length=settings.MAX_LEN_USERS_FIELD,
        verbose_name='Фамилия',
        help_text=texts.HELP_LAST_NAME,
    )

    email = models.EmailField(
        max_length=settings.MAX_LEN_EMAIL_FIELD,
        unique=True,
        help_text=texts.HELP_EMAIL,
    )

    password = models.CharField(
        max_length=settings.MAX_LEN_USERS_FIELD,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'password',
        'first_name',
        'last_name',
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'username'],
                name='unique_auth'
            )
        ]

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'


class Follow(models.Model):
    '''Подписка пользователей друг на друга.'''

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'following'),
                name='Вы уже подписаны на этого автора'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('following')),
                name='Нельзя подписаться на себя'
            ),
        )
        ordering = ['-id']

    def __str__(self) -> str:
        return f'{self.following} подписан на {self.author}'
