from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

from .paginations import CategoryPagination, GenrePagination
from .permissions import (CanCreateReview, IsAdminOrReadOnly, IsAnonymous,
                          IsAuthor, IsModerator, IsModeratorOrOwner,
                          IsSuperUserOrIsAdmin)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          TokenCreateSerializer, UserCreateSerializer,
                          UserSerializer)
from .utils import send_confirmation_code


class UserViewSet(viewsets.ModelViewSet):
    """Представление для взаимодействия с пользователем, создание
    пользователя администратором, удаление/изменение/получение пользователя.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username', )
    permission_classes = (IsSuperUserOrIsAdmin, )

    @action(
        detail=False,
        methods=['get', 'patch', 'delete'],
        url_path=r'(?P<username>[\w.@+-]+)'
    )
    def user_by_username(self, request, username):
        """Изменение данных учетной записи конкретного пользователя."""

        user = get_object_or_404(User, username=username)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=(permissions.IsAuthenticated, )
    )
    def user_by_me(self, request):
        """Изменение данных своей учетной записи."""
        if request.method == 'PATCH':
            data = request.data.copy()
            data.pop('role', None)
            serializer = UserSerializer(
                request.user, data=data, partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Представление для работы с пользователем, создание пользователя
    самостоятельно.
    """

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (permissions.AllowAny, )

    def create(self, request):
        """Создание пользователя и генерация кода поддтверждения
        через email.
        """
        serializer = UserCreateSerializer(data=request.data)
        user = User.objects.filter(
            username=request.data.get('username')
        ).first()
        if user:
            if user.email == serializer.initial_data.get('email'):
                confirmation_code = default_token_generator.make_token(user)
                send_confirmation_code(user.email, confirmation_code)
                return Response(
                    {
                        'message': (
                            'Пользователь уже существует. '
                            'Код подтверждения отправлен повторно.'
                        )
                    },
                    status=status.HTTP_200_OK
                )
            else:
                error = {
                    'email': 'Email не соответствует данному пользователю.'
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create(**serializer.validated_data)
        confirmation_code = default_token_generator.make_token(user)
        send_confirmation_code(user.email, confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Представление для работы с токеном."""

    queryset = User.objects.all()
    serializer_class = TokenCreateSerializer
    permission_classes = (permissions.AllowAny, )

    def create(self, request):
        """Генерация токена на основе кода подтверждения."""

        serializer = TokenCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.validated_data.get('confirmation_code')
        if not default_token_generator.check_token(user, confirmation_code):
            message = {'token': 'Ошибка валидации токена.'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        access_token = str(AccessToken.for_user(user))
        message = {'token': access_token}
        return Response(message, status=status.HTTP_200_OK)


class BaseViewSet(
        mixins.DestroyModelMixin,
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'slug']
    search_fields = ('name', 'slug',)
    permission_classes = (IsSuperUserOrIsAdmin | IsAnonymous,)
    lookup_field = 'slug'


class CategoryViewSet(BaseViewSet):
    queryset = Category.objects.all().order_by('slug')
    serializer_class = CategorySerializer


class GenreViewSet(BaseViewSet):
    queryset = Genre.objects.all().order_by('slug')
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().order_by('name')
    permission_classes = (IsSuperUserOrIsAdmin | IsAnonymous,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')
    search_fields = ('category__slug', 'genre__slug', 'name', 'year',)

    def get_queryset(self):
        queryset = super().get_queryset()
        if 'genre' in self.request.query_params:
            self.pagination_class = GenrePagination
        elif 'category' in self.request.query_params:
            self.pagination_class = CategoryPagination
        return queryset

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return TitleWriteSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с отзывами.
    """
    serializer_class = ReviewSerializer

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (CanCreateReview,)
        # Для PATCH и DELETE разрешаем доступ автору, модератору или админу
        elif self.request.method in ['PATCH', 'DELETE']:
            self.permission_classes = (
                IsModeratorOrOwner,
                IsAdminOrReadOnly
            )
        elif self.request.method == 'GET':
            self.permission_classes = (IsAnonymous,)
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
        elif self.request.method == 'GET':
            self.permission_classes = (IsAnonymous,)

        return super().get_permissions()

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')

        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)
