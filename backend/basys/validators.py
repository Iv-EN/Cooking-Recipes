from re import compile
from string import hexdigits

from django.core.exceptions import ValidationError


def validate_name(name: str):
    '''Проверка имени пользователя на содержание недопустимых знаков.'''
    pattern = compile(r'[\w.@+-]+')
    invalid_chars = pattern.sub('', name)
    invalid_chars = ''.join(set(invalid_chars))
    if invalid_chars:
        raise ValidationError(
            f'Символы "{invalid_chars}" использовать нельзя!'
        )
    return name


def color_validator(color: str) -> str:
    '''Проверка кодировки цвета на соответствие HEX.'''
    color = color.strip(' #')
    if len(color) not in (3, 6):
        raise ValidationError(
            f'Код цвета {color} неправильной длины ({len(color)}).'
        )
    if not set(color).issubset(hexdigits):
        raise ValidationError(f'{color} - не шестнадцатиричное значение.')
    if len(color) == 3:
        return f'#{color[0] * 2}{color[1] * 2}{color[2] * 2}'.upper()
    return '#' + color.upper()
