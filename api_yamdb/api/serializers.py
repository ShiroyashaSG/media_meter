from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

from api_yamdb.constants import (MAX_LENGTH_EMAIL, MAX_LENGTH_NAME,
                                 MIN_SCORE_VALUE, MAX_SCORE_VALUE)


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
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )
        ]
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class UserCreateSerializer(UserMixin, serializers.ModelSerializer):
    """Сериализатор пользователя, регистрируемого самостоятельно."""

    class Meta:
        model = User
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )
        ]
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
    """Сериализатор жанра."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории."""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор произведения для чтения."""
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор произведения для записи."""
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review.

    Обрабатывает данные отзыва, включая валидацию рейтинга и уникальности отзыва
    для каждого произведения (title) от каждого пользователя (author).
    """
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ['id', 'text', 'author', 'score', 'pub_date']

    def validate_score(self, value):
        """
        Проверяет, что рейтинг находится в пределах от MIN_SCORE_VALUE до
        MAX_SCORE_VALUE.

        Args:
            value (int): Рейтинг отзыва.

        Raises:
            serializers.ValidationError: Если рейтинг вне допустимого
            диапазона.
        """
        if value < MIN_SCORE_VALUE or value > MAX_SCORE_VALUE:
            raise serializers.ValidationError(
                'Рейтинг должен быть от MIN_SCORE_VALUE до MAX_SCORE_VALUE.'
            )
        return value

    def validate(self, data):
        """
        Проверяет данные перед сохранением, включая уникальность отзыва
        для текущего произведения и пользователя.

        Args:
            data (dict): Данные отзыва.

        Raises:
            serializers.ValidationError: Если отзыв от текущего пользователя
            на это произведение уже существует.
        """
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
    """
    Сериализатор для модели Comment.

    Обрабатывает данные комментария, включая валидацию на наличие
    соответствующего отзыва и произведения.
    """
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'pub_date']

    # def validate(self, data):
    #     """
    #     Выполняет валидацию данных комментария, проверяя наличие отзыва и его
    #     принадлежность произведению.

    #     Метод проверяет, что отзыв (Review), к которому относится создаваемый
    #     или редактируемый комментарий, существует и принадлежит переданному
    #     произведению (Title).
    #     Если проверка не пройдена, выбрасывается ошибка валидации.

    #     Args:
    #         data (dict): Входные данные для сериализатора, содержащие данные
    #         комментария.

    #     Returns:
    #         dict: Валидированные данные.

    #     Raises:
    #         ValidationError: Если отзыв не найден или если отзыв не
    #         принадлежит указанному произведению.
    #     """
    #     title = self.context['title']  # Получаем объект Title из контекста
    #     review = self.context['review']  # Получаем объект Review из контекста

    #     # Получаем список всех отзывов для данного произведения
    #     reviews_for_title = Review.objects.filter(
    #         title_id=title.id
    #     ).values_list('id', flat=True)

    #     # Проверяем, что данный review_id принадлежит этому title
    #     if review.id not in reviews_for_title:
    #         raise serializers.ValidationError('Этот отзыв не принадлежит к '
    #                                           'данному произведению.')

    #     return data

    def validate(self, data):
        """
        Проверяет данные перед сохранением, включая наличие отзыва
        и соответствующего произведения.

        Args:
            data (dict): Данные комментария.

        Raises:
            NotFound: Если отзыв или произведение не найдены.
        """
        title = self.context['title']
        review = self.context['review']

        # review = Review.objects.filter(id=review.id, title=title).first()
        # if not review:
        #     raise NotFound("Отзыв не найден для данного произведения.")
        
        if review.title.id != title.id:  # Проверка на принадлежность
            raise NotFound("Отзыв не принадлежит этому произведению.")

        return data
