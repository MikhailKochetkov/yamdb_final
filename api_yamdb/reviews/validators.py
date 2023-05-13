from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError

ERROR_USERNAME_RESERVED = ("'{value}' нельзя использовать в качестве "
                           "имени пользователя")
ERROR_USERNAME_SYMBOL = "Нельзя использовать символы '{}' в username"
ERROR_MAX_YEAR = ('Год выпуска не может превышать'
                  ' {max_year} год! Ваш год: {value}')


def validate_non_reserved(value):
    if value in settings.RESERVED_USERNAMES:
        raise ValidationError(ERROR_USERNAME_RESERVED.format(value=value))
    return value


def validate_username_allowed_chars(value):
    invalid_chars = ''.join(set(settings.USERNAME_VALID_PATTERN.sub('', value)))
    if invalid_chars:
        raise ValidationError(
            ERROR_USERNAME_SYMBOL.format(invalid_chars)
        )
    return value


def validate_max_year(value):
    max_year = datetime.now().year
    if value > max_year:
        raise ValidationError(
            ERROR_MAX_YEAR.format(max_year=max_year, value=value)
        )
    return value
