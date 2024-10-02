from django.urls import include, path
from rest_framework.routers import DefaultRouter
from reviews.views import ReviewViewSet, CommentViewSet, MockTitleViewSet

router = DefaultRouter()
router.register(r'titles', MockTitleViewSet, basename='mocktitle')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='review')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
                CommentViewSet, basename='comment')

urlpatterns = [
    path('v1/', include(router.urls)),
]
