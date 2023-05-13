from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from reviews.validators import (
    validate_non_reserved,
    validate_username_allowed_chars,
    validate_max_year
)

ROLES_CHOICES = (
    (settings.ROLE_USER, 'Пользователь'),
    (settings.ROLE_MODERATOR, 'Модератор'),
    (settings.ROLE_ADMIN, 'Администратор'),
)


class User(AbstractUser):
    username = models.CharField(
        unique=True,
        max_length=settings.USERNAME_MAX_LENGTH,
        validators=(
            validate_non_reserved,
            validate_username_allowed_chars
        )
    )
    email = models.EmailField(
        unique=True,
        max_length=settings.EMAIL_MAX_LENGTH
    )
    role = models.CharField(
        choices=ROLES_CHOICES,
        default=settings.ROLE_USER,
        max_length=max(len(role) for role,_ in ROLES_CHOICES)
    )
    bio = models.TextField(blank=True, null=True)
    confirmation_code = models.CharField(
        max_length=settings.CONFIRMATION_CODE_LENGTH,
        blank=True,
        null=True
    )
    first_name = models.CharField(
        max_length=settings.FIRST_NAME_MAX_LENGTH,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        max_length=settings.LAST_NAME_MAX_LENGTH,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == settings.ROLE_MODERATOR

    @property
    def is_admin(self):
        return (self.role == settings.ROLE_ADMIN) or self.is_staff


class CategoryGenreBaseModel(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Идентификатор'
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(CategoryGenreBaseModel):
    class Meta(CategoryGenreBaseModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryGenreBaseModel):
    class Meta(CategoryGenreBaseModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    year = models.PositiveIntegerField(
        validators=(validate_max_year,),
        verbose_name='Год выпуска'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles',
        verbose_name='Жанры'
    )
    description = models.TextField()

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre_id = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    title_id = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['genre_id', 'title_id'],
                name='unique genre title'
            )
        ]

    def __str__(self):
        return f'{self.genre_id} - {self.title_id}'


class TextAuthorDateBaseModel(models.Model):
    text = models.TextField(
        verbose_name='Текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        abstract = True

    def __str__(self):
        return (
            f'{self.author} - {self.pub_date} - {self.text[:settings.LEN_TXT]}'
        )


class Review(TextAuthorDateBaseModel):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    score = models.IntegerField(
        verbose_name='Оценка произведения',
        validators=(MinValueValidator(1), MaxValueValidator(10))
    )

    class Meta(TextAuthorDateBaseModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_title_author'
            )
        ]


class Comment(TextAuthorDateBaseModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta(TextAuthorDateBaseModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
