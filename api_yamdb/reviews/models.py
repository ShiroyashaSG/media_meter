from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator
from django.utils import timezone

from .constans import MAX_LENGTH, LIMIT_LENGTH


class BaseModel(models.Model):
    """Базовая модель."""
    name = models.CharField(max_length=MAX_LENGTH, verbose_name="Название")
    slug = models.SlugField(
        max_length=LIMIT_LENGTH,
        unique=True,
        verbose_name="Slug",
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message="Slug может содержать только буквы,"
            + "цифры, дефисы и символы подчеркивания."
        )]
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Genre(BaseModel):
    """Модель жанра."""
    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Category(BaseModel):
    """Модель категории."""
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Title(models.Model):
    """Модель произведения."""
    name = models.CharField(max_length=MAX_LENGTH, verbose_name="Название")
    year = models.PositiveIntegerField(
        verbose_name="Год выпуска",
        validators=[MaxValueValidator(timezone.now().year)],
    )
    description = models.TextField(
        null=True, blank=True, verbose_name="Описание"
    )
    genre = models.ManyToManyField(
        Genre, verbose_name="Жанры", related_name="titles"
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.SET_NULL,
        null=True,
        related_name="titles"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
