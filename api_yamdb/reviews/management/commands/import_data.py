import csv
import os

import pandas
from django.conf import settings
from django.core.management import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class Command(BaseCommand):
    """Команда для импорта данных из csv."""
    def handle(self, *args, **kwargs):
        self.import_genres()
        self.import_categories()
        self.import_titles()
        self.import_users()
        self.import_reviews()
        self.import_comments()
        self.import_genre_title()

    def import_genres(self):
        data_path = os.path.join(settings.BASE_DIR, 'static/data/genre.csv')
        df = pandas.read_csv(data_path)
        for _, row in df.iterrows():
            genre, created = Genre.objects.get_or_create(
                name=row['name'],
                slug=row['slug']
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Жанр "{genre.name}" создан.')
                )
            else:
                self.stdout.write(f'Жанр "{genre.name}" уже существует.')

    def import_categories(self, *args, **kwargs):
        data_path = os.path.join(settings.BASE_DIR, 'static/data/category.csv')
        df = pandas.read_csv(data_path)
        for _, row in df.iterrows():
            category, created = Category.objects.get_or_create(
                id=row['id'],
                name=row['name'],
                slug=row['slug']
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Категория "{category.name}" создана.')
                )
            else:
                self.stdout.write(
                    f'Категория "{category.name}" уже существует'
                )

    def import_titles(self):
        data_path = os.path.join(settings.BASE_DIR, 'static/data/titles.csv')
        df = pandas.read_csv(data_path)

        for _, row in df.iterrows():
            category_id = row['category']
            category = Category.objects.get(id=category_id)
            title, created = Title.objects.get_or_create(
                name=row['name'],
                year=row['year'],
                category=category
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Название "{title.name}" создано.')
                )
            else:
                self.stdout.write(
                    f'Название "{title.name}" уже существует.'
                )

    def import_users(self):
        data_path = os.path.join(settings.BASE_DIR, 'static/data/users.csv')
        df = pandas.read_csv(data_path)
        for _, row in df.iterrows():
            user, created = User.objects.get_or_create(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                defaults={
                    'role': row.get('role', 'user'),
                    'bio': row.get('bio', ''),
                    'first_name': row.get('first_name', ''),
                    'last_name': row.get('last_name', ''),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Пользователь "{user.username}" создан.')
                )
            else:
                self.stdout.write(
                    f'Пользователь "{user.username}" уже существует.'
                )

    def import_reviews(self):
        data_path = os.path.join(settings.BASE_DIR, 'static/data/review.csv')
        df = pandas.read_csv(data_path)
        for _, row in df.iterrows():
            author_id = row['author']
            user = User.objects.get(id=author_id)
            review, created = Review.objects.get_or_create(
                title_id=row['title_id'],
                text=row['text'],
                author=user,
                score=row['score'],
                pub_date=row['pub_date']
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Отзыв создан для названия с ID "{row["title_id"]}".')
                )
            else:
                self.stdout.write(
                    'Отзыв уже существует для'
                    + f'названия с ID "{row["title_id"]}".'
                )

    def import_comments(self):
        data_path = os.path.join(settings.BASE_DIR, 'static/data/comments.csv')
        df = pandas.read_csv(data_path)
        for _, row in df.iterrows():
            author_id = row['author']
            user = User.objects.get(id=author_id)
            comment, created = Comment.objects.get_or_create(
                review_id=row['review_id'],
                text=row['text'],
                author=user,
                pub_date=row['pub_date']
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        'Комментарий создан для'
                        + f'отзыва с ID "{row["review_id"]}".'
                    )
                )
            else:
                self.stdout.write(
                    'Комментарий уже существует для'
                    + f'отзыва с ID "{row["review_id"]}".'
                )

    def import_genre_title(self):
        data_path = os.path.join(
            settings.BASE_DIR, 'static/data/genre_title.csv'
        )
        df = pandas.read_csv(data_path)
        for _, row in df.iterrows():
            # Проверяем существование title и genre перед созданием связи
            try:
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                title.genre.add(genre)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Связь между произведением ID "{title.id}"'
                        + f'и жанром ID "{genre.id}" создана.'
                    )
                )
            except Title.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'Произведение с ID "{row["title_id"]}" не существует.'
                    )
                )
            except Genre.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'Жанр с ID "{row["genre_id"]}" не существует.'
                    )
                )
