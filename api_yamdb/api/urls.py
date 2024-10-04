from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, GenreViewSet, TitleViewSet,
    UserViewSet, UserCreateViewSet, TokenCreateViewSet
)

router_v1 = DefaultRouter()

router_v1.register('titles', TitleViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register('categories', CategoryViewSet)
router_v1.register('users', UserViewSet)

urlpatterns = [
    path("v1/", include(router_v1.urls)),
    path(
        'v1/auth/signup/',
        UserCreateViewSet.as_view({'post': 'create'}),
        name='signup'
    ),
    path(
        'v1/auth/token/',
        TokenCreateViewSet.as_view({'post': 'create'}),
        name='token'
    )
]
