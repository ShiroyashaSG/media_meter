from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from users.models import User
from reviews.models import Category, Genre, Title, Review, Comment
from api_yamdb.constants import (
    MAX_LENGTH_EMAIL, MAX_LENGTH_NAME
)


class UserMixin:
    """Миксин для сериализатора пользователя."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=MAX_LENGTH_NAME,
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Пользователь с таким именем username уже существует.'
        )],
        error_messages={
            'invalid': (
                'Имя пользователя может содержать только буквы, цифры ',
                'и символы @/./+/-/_'
            )
        }
    )
    email = serializers.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким именем email уже существует.'
            )
        ]
    )

    def validate_username(self, username):
        """Влидация поля username на доступность использования 'me' в качестве
        username пользователя.
        """

        if username == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать \'me\' в качестве username.'
            )
        return username


class UserSerializer(UserMixin, serializers.ModelSerializer):
    """Сериализатор пользователя, регистрируемого администратором."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class UserCreateSerializer(UserMixin, serializers.ModelSerializer):
    """Сериализатор пользователя, регистрируемого самостоятельно."""

    class Meta:
        model = User
        fields = ('username', 'email')


class TokenCreateSerializer(serializers.Serializer):
    """Сериализатор токена."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=MAX_LENGTH_NAME,
        required=True
    )
    confirmation_code = serializers.CharField(
        required=True
    )


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug', queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ['id', 'text', 'author', 'score', 'pub_date']

    def validate_score(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError(
                'Рейтинг должен быть от 1 до 10.'
            )
        return value

    def validate(self, data):
        request = self.context['request']
        title = self.context.get('title')

        if (
            request.method == 'POST'
            and Review.objects.filter(
                title=title.id,
                author=request.user
            ).exists()
        ):
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение.'
            )

        data['title'] = title
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'pub_date']

    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')
        review_id = self.context['view'].kwargs.get('review_id')
        get_object_or_404(Title, id=title_id)
        if not Review.objects.filter(id=review_id).exists():
            raise ValidationError("Отзыв не найден.")
        return data
