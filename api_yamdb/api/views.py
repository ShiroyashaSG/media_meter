from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from reviews.models import Category, Genre, Title

from .serializers import CategorySerializer, GenreSerializer, TitleSerializer


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
