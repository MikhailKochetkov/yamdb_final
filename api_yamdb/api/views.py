import random

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin
)
from rest_framework.permissions import (
    AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
)
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilterSet
from api.permissions import AdminOrReadOnly, AdminOnly, AuthorOrStuffOrReadOnly
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    GetTitleSerializer,
    PostTitleSerializer,
    SignupSerializer,
    TokenObtainSerializer,
    UserSerializer,
    ReviewSerializer,
    CommentSerializer
)
from reviews.models import Category, Genre, Title, Review, User

ERROR_CONFIRMATION_CODE = 'Неверный код подтверждения, получите новый'
ERROR_SIGNUP_USERNAME_MAIL_TAKEN = (
    'Пользователь с таким email или username уже существует'
)


def get_code():
    return ''.join(
        random.choices(
            population=settings.CONFIRMATION_CODE_CHARS,
            k=settings.CONFIRMATION_CODE_LENGTH,
        )
    )


def send_email(user_email, code):
    send_mail(
        subject=settings.DEFAULT_SUBJECT,
        message=settings.DEFAULT_MESSAGE.format(code),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email]
    )


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        try:
            user, created = User.objects.get_or_create(
                username=username,
                email=email
            )
        except IntegrityError:
            raise ValidationError(ERROR_SIGNUP_USERNAME_MAIL_TAKEN)
        user.confirmation_code = get_code()
        user.save()
        send_email(user.email, user.confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryGenreViewSet(
    CreateModelMixin, ListModelMixin,
    DestroyModelMixin, GenericViewSet
):
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = [AdminOrReadOnly]


class CategoryViewSet(CategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = PostTitleSerializer
    filterset_class = TitleFilterSet
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    permission_classes = [AdminOrReadOnly]
    ordering = ('name',)
    ordering_fields = ('name',)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return PostTitleSerializer
        return GetTitleSerializer


class TokenObtainAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.validated_data['username']
        )
        if ((user.confirmation_code != settings.RESET_CODE_VALUE)
                or (serializer.validated_data['confirmation_code']
                    != user.confirmation_code)):
            user.confirmation_code = settings.RESET_CODE_VALUE
            user.save()
            raise ValidationError(ERROR_CONFIRMATION_CODE)
        return Response(
            {
                'token': str(
                    RefreshToken.for_user(user).access_token
                )
            }, status=status.HTTP_200_OK
        )


class UserViewSet(ModelViewSet):
    filter_backends = (SearchFilter,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AdminOnly]
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete')


class UserMeAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(
            UserSerializer(instance=request.user).data,
            status=status.HTTP_200_OK
        )

    def patch(self, request):
        serializer = UserSerializer(
            instance=request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=serializer.instance.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorOrStuffOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorOrStuffOrReadOnly,)

    def get_review_object(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        review = self.get_review_object()
        return review.comments.all()

    def perform_create(self, serializer):
        new_review = self.get_review_object()
        serializer.save(author=self.request.user, review=new_review)
