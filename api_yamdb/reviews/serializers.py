from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Comment, Review, MockTitle


class MockTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MockTitle
        fields = ['id', 'name', 'description']


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ['id', 'title', 'author', 'text', 'score', 'pub_date']

    def validate_score(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError(
                'Рейтинг должен бытьот 1 до 10.'
            )
        return value

    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')
        if not MockTitle.objects.filter(id=title_id).exists():
            raise ValidationError("Произведение не найдено.")
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
