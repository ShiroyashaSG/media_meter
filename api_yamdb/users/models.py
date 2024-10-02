from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, EmailValidator
from django.db import models


class Role(Enum):
    """Поле перечисления ролей пользователей."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        db_index=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message='Недопустимый символ в имени пользователя.'
        )]
    )
    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким email уже существует.',
            'invalid': 'Введите корректный email адрес.',
            'blank': 'Это поле не может быть пустым.'
        }
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=[(role.value, role.name) for role in Role],
        default=Role.USER.value,
        help_text='Admin, moderator или user. По-умолчанию user.'
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id', )

    def __str__(self) -> str:
        return self.username

    @property
    def is_admin(self):
        return self.role == Role.ADMIN.name

    @property
    def is_moderator(self):
        return self.role == Role.MODERATOR.name

    @property
    def is_user(self):
        return self.role == Role.USER.name
