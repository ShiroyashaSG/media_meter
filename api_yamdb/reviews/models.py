from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

# from .models import Title  # предполагается, что модель Title создана


User = get_user_model()


class MockTitle(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(MockTitle, on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField()
    author_id = models.IntegerField(blank=True, null=True)
    # author = models.ForeignKey(User, on_delete=models.CASCADE,
                            #    related_name='reviews')
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],  # Ограничение от 1 до 10
        help_text="Оценка от 1 до 10."
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('author_id', 'title')  # Один отзыв от пользователя на одно произведение
        # unique_together = ('author', 'title')  # Один отзыв от пользователя на одно произведение
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
        ordering = ['pub_date']  # Упорядочивание по дате публикации

    def __str__(self):
        return f'{self.author} комментирует {self.review}'
