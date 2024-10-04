from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet, UserCreateViewSet, TokenCreateViewSet,
    ReviewViewSet, CommentViewSet, CategoryViewSet,
    GenreViewSet, TitleViewSet
)

router_v1 = DefaultRouter()

router_v1.register("titles", TitleViewSet)
router_v1.register("genres", GenreViewSet)
router_v1.register("categories", CategoryViewSet)
router_v1.register("users", UserViewSet)

router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comment'
)


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
