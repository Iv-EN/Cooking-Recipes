from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from core import texts
from core.validators import ValidateName


class CustomUser(AbstractUser):
    """Пользователь."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')
    username = models.CharField(
        verbose_name='Логин',
        max_length=settings.MAX_LEN_USERS_FIELD,
        unique=True,
        error_messages={
            'unique': 'Логин занят.'
        },
        validators=[ValidateName(field='Имя пользователя')],
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
        verbose_name='e-mail',
        max_length=settings.MAX_LEN_EMAIL_FIELD,
        unique=True,
        error_messages={
            'unique': 'Пользователь с данным e-mail уже зарегестрирован.'
        },
        help_text=texts.HELP_EMAIL,
    )

    password = models.CharField(
        verbose_name='Пароль',
        max_length=settings.MAX_LEN_USERS_FIELD,
    )

    is_active = models.BooleanField(
        verbose_name='Активирован',
        default=True,
    )

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


class Subscriptions(models.Model):
    """Подписка пользователей друг на друга."""

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор рецепта',
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
    )
    date_added = models.DateTimeField(
        verbose_name='Дата создания подписки',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='You_are_already_subscribed_to_this_author',
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name="You_can't_follow_yourself",
            ),
        )
        ordering = ['-id']

    def __str__(self) -> str:
        return f'{self.user.username} подписан на {self.author.username}'
