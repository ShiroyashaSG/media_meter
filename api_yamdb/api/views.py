from rest_framework import viewsets, filters
from reviews.models import Review, Comment, Category, Genre, Title
from django.shortcuts import get_object_or_404
from .permissions import (IsModeratorOrOwner, IsAdminOrReadOnly,
                          CanCreateReview)

from .serializers import (ReviewSerializer, CommentSerializer,
                          CategorySerializer, GenreSerializer, TitleSerializer)
from reviews.models import Title
from django_filters.rest_framework import DjangoFilterBackend


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с отзывами.
    """
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (CanCreateReview,)
        # Для PATCH и DELETE разрешаем доступ автору, модератору или админу
        elif self.request.method in ['PATCH', 'DELETE']:
            self.permission_classes = (
                IsModeratorOrOwner,
                IsAdminOrReadOnly
            )
        return super().get_permissions()

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        get_object_or_404(Title, id=title_id)
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с комментариями.
    """
    serializer_class = CommentSerializer

    def get_permissions(self):
        # Для POST-запросов используем пермишен для создания комментариев
        if self.request.method == 'POST':
            self.permission_classes = (CanCreateReview,)
        # Для PATCH и DELETE разрешаем доступ автору, модератору или админу
        elif self.request.method in ['PATCH', 'DELETE']:
            self.permission_classes = (
                IsModeratorOrOwner,
                IsAdminOrReadOnly
            )
        return super().get_permissions()

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)

class BaseViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'slug']
    search_fields = ('name', 'slug')


class CategoryViewSet(BaseViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'year', 'category', 'genre']
    search_fields = ('name', 'year', 'category', 'genre')
