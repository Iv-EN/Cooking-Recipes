from re import compile
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

if TYPE_CHECKING:
    from recipes.models import Ingredient, Tag


@deconstructible
class ValidateName:
    """Проверка имени пользователя"""

    def __init__(
        self,
        forbiden_symbols: str = r'[^а-яёА-ЯЁa-zA-Z0-9]',
        field: str = 'Переданное значение'
    ) -> None:
        self.forbidden_symbols = compile(forbiden_symbols)
        self.field = field

    def __call__(self, value: str) -> None:
        if self.forbidden_symbols.search(value):
            raise ValidationError(
                f'{self.field} содержит запрещённые символы!'
            )
        сyrillic_alphabet = any(
            ord(char) >= 0x0400 and ord(char) <= 0x04FF for char in value
        )
        latin_alphabet = any(
            ord(char) >= 0x0041 and ord(char) <= 0x007A for char in value
        )
        if сyrillic_alphabet and latin_alphabet:
            raise ValidationError(
                f'{self.field} содержит буквы из разных алфавитов.'
            )


class ColorValidator:
    def __init__(self) -> None:
        self.hexdigits = set('0123456789abcdefABCDEF')

    def validate(self, color: str) -> str:
        """Проверка кодировки цвета на соответствие HEX."""
        color = color.strip(' #')
        if len(color) not in (3, 6):
            raise ValidationError(
                f'Код цвета {color} неправильной длины ({len(color)}).'
            )
        if not set(color).issubset(self.hexdigits):
            raise ValidationError(f'{color} - не шестнадцатиричное значение.')
        if len(color) == 3:
            return f'#{color[0] * 2}{color[1] * 2}{color[2] * 2}'.upper()
        return '#' + color.upper()


class TagsValidator:
    @staticmethod
    def validate(tags_ids, Tag) -> list['Tag']:
        """Проверка существования тэгов с указанными id."""
        if not tags_ids:
            raise ValidationError('Тэгов нет')
        tags = Tag.objects.filter(id__in=tags_ids)
        if tags.count() != len(tags_ids):
            raise ValidationError('Указанный тэг не существует')
        return tags


class IngredientsValidator:
    def __init__(self, Ingredients, Ingredient) -> None:
        self.Ingredients = Ingredients
        self.Ingredient = Ingredient

    def validate(
        ingredients: list[dict[str, str | int]],
        Ingredient: 'Ingredient',
    ) -> dict[int, tuple['Ingredient', int]]:
        """Проверка списка ингредиентов."""
        if not ingredients:
            raise ValidationError('Не указано ни одного ингредиента')
        valid_ingredients = {}
        for ingredient in ingredients:
            if not (isinstance(ingredient['amount'], int)
                    or ingredient['amount'].isdigit()):
                raise ValidationError('Проверьте количество ингредиента')
            valid_ingredients[ingredient['id']] = int(ingredient['amount'])
            if valid_ingredients[ingredient['id']] <= 0:
                raise ValidationError('Проверьте количество ингредиента')
        if not valid_ingredients:
            raise ValidationError('Неправильные ингредиенты')
        db_inredients = Ingredient.objects.filter(
            pk__in=valid_ingredients.keys())
        if not db_inredients:
            raise ValidationError('Неправильные ингредиенты')
        for ingredient in db_inredients:
            valid_ingredients[ingredient.pk] = (
                ingredient, valid_ingredients[ingredient.pk])
        return valid_ingredients
