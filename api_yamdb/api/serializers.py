from django.conf import settings
from django.core.validators import (
    MinValueValidator, MaxValueValidator
)
from django.shortcuts import get_object_or_404
from rest_framework.serializers import (
    CharField,
    EmailField,
    IntegerField,
    ModelSerializer,
    Serializer,
    SlugRelatedField,
    ValidationError
)

from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import (
    validate_username_allowed_chars,
    validate_max_year,
    validate_non_reserved
)

REGEX_VALIDATION_MESSAGE = (
    'Введите правильное имя пользователя.'
    ' Оно может содержать только буквы, цифры и знаки @/./+/-/_.'
)
ERROR_SIGNUP_EMAIL = 'Неправильно указан email'
ERROR_SIGNUP_USERNAME_MAIL_TAKEN = (
    'Пользователь с таким e-mail уже существует или неверный username'
)
ERROR_SIGNUP_USERNAME_OR_EMAIL = 'Неверный username или e-mail'

ERROR_REVIEW_AUTHOR_UNIQUE = (
    'Нельзя оставлять несколько отзывов на одно произведение'
)


class UsernameValidationMixin:
    def validate_username(self, value):
        value = validate_non_reserved(value)
        validate_username_allowed_chars(value)
        return value


class SignupSerializer(Serializer, UsernameValidationMixin):
    username = CharField(
        required=True,
        max_length=settings.USERNAME_MAX_LENGTH,
    )
    email = EmailField(
        required=True,
        max_length=settings.EMAIL_MAX_LENGTH,
    )


class ReviewSerializer(ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    score = IntegerField(
        validators=(MinValueValidator(1), MaxValueValidator(10))
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)

    def validate(self, data):
        if self.context.get('request').method != 'POST':
            return data
        reviewer = self.context.get('request').user
        if get_object_or_404(
                Title, id=self.context.get('view').kwargs.get('title_id')
        ).reviews.filter(author=reviewer):
            raise ValidationError(ERROR_REVIEW_AUTHOR_UNIQUE)
        return data


class CommentSerializer(ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class GetTitleSerializer(ModelSerializer):
    category = CategorySerializer(many=False, required=True)
    genre = GenreSerializer(many=True, required=False)
    rating = IntegerField()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        read_only_fields = fields


class PostTitleSerializer(ModelSerializer):
    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        many=False
    )
    genre = SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        required=False
    )
    year = IntegerField(
        validators=(validate_max_year,)
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        extra_kwargs = {'description': {'required': False}}


class TokenObtainSerializer(Serializer, UsernameValidationMixin):
    username = CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        required=True,
    )
    confirmation_code = CharField(
        required=True,
    )


class UserSerializer(ModelSerializer, UsernameValidationMixin):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
