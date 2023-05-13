from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    SignupView, TokenObtainAPIView, UserViewSet, UserMeAPIView,
    CategoryViewSet, GenreViewSet, TitleViewSet, CommentViewSet, ReviewViewSet
)

URL_COMMENTS = r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments'
URL_REVIEW = r'titles/(?P<title_id>\d+)/reviews'

auth_urls = [
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/token/', TokenObtainAPIView.as_view(), name='token'),
]

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='user')
router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(r'genres', GenreViewSet, basename='genres')
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(URL_COMMENTS, CommentViewSet, basename='comment')
router_v1.register(URL_REVIEW, ReviewViewSet, basename='review')

urlpatterns = [
    path('v1/users/me/', UserMeAPIView.as_view(), name='self'),
    path('v1/', include(router_v1.urls)),
    path('v1/', include(auth_urls))
]
