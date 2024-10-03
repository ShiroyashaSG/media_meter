from rest_framework import viewsets, permissions, status
from reviews.models import Review, Comment
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .permissions import IsAuthorOrReadOnly
from .serializers import (ReviewSerializer, CommentSerializer,)
from reviews.models import Title


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с отзывами.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = Review.objects.get(id=review_id)
        serializer.save(author=self.request.user, review=review)

    def partial_update(self, request, *args, **kwargs):
        """
        Частичное обновление комментария.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Удаление комментария.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
