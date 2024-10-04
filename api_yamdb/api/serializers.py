from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from reviews.models import Comment, Review, Title, Category, Genre
from django.shortcuts import get_object_or_404


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
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)

        # Проверяем, оставил ли пользователь уже отзыв на это произведение
        if Review.objects.filter(title=title.id, author=request.user).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение.'
            )

        # Присваиваем title, чтобы сохранить его позже
        data['title'] = title.id
        # data['title'] = title
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ['id', 'review', 'author', 'text', 'pub_date']

    def validate(self, data):
        review_id = self.context['view'].kwargs.get('review_id')
        if not Review.objects.filter(id=review_id).exists():
            raise ValidationError("Отзыв не найден.")
        return data


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
