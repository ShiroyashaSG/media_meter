from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import (MinValueValidator, MaxValueValidator,
                                    RegexValidator)

from django.utils import timezone
from .constans import LIMIT_LENGTH, MAX_LENGTH


User = get_user_model()


class Title(models.Model):
    pass


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='reviews')
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],  # Ограничение от 1 до 10
        help_text="Оценка от 1 до 10."
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('author', 'title')  # Один отзыв от пользователя на одно произведение
        ordering = ['-pub_date']  # Упорядочивание по дате публикации

    def __str__(self):
        return f'{self.author_id} — {self.title} ({self.score})'


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        return f'{self.author} комментирует {self.review}'


class BaseModel(models.Model):
    '''Базовая модель.'''
    name = models.CharField(max_length=MAX_LENGTH, verbose_name='Название')
    slug = models.SlugField(
        max_length=LIMIT_LENGTH,
        unique=True,
        verbose_name='Slug',
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Slug может содержать только буквы,'
                    + 'цифры, дефисы и символы подчеркивания.'
        )]
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Genre(BaseModel):
    '''Модель жанра.'''
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(BaseModel):
    '''Модель категории.'''
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    '''Модель произведения.'''
    name = models.CharField(max_length=MAX_LENGTH, verbose_name='Название')
    year = models.PositiveIntegerField(
        verbose_name='Год выпуска',
        validators=[MaxValueValidator(timezone.now().year)],
    )
    description = models.TextField(
        null=True, blank=True, verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre, verbose_name='Жанры', related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
