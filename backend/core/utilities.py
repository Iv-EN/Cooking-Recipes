"""Вспомогательные утилиты."""
from django.conf import settings
from datetime import datetime as dt
from typing import TYPE_CHECKING
from urllib.parse import unquote

from django.db.models import F, Sum

from recipes.models import AmountIngredient, Recipe

if TYPE_CHECKING:
    from recipes.models import Ingredient
    from users.models import CustomUser


def recipe_ingredients_set(
        recipe: Recipe, ingredients: dict[int, tuple['Ingredient', int]]
) -> None:
    """Запись ингредиентов рецепта."""
    objs = []
    for ingredient, amount in ingredients.values():
        objs.append(
            AmountIngredient(
                recipe=recipe, ingredients=ingredient, amount=amount
            )
        )
    AmountIngredient.objects.bulk_create(objs)


def create_shoping_list(user: 'CustomUser') -> str:
    """Формирование списка продуктов для покупки."""
    shopping_list = [
        f'Список покупок для пользователя: {user.first_name}'
        f'\n{dt.now().strftime(settings.DATETIME_FORMAT)}\n'
    ]
    ingredients = (
        AmountIngredient.objects.filter(recipe__in_basket__user=user)
        .values('ingredients__name',
                measurement=F('ingredients__measurement_unit'))
        .annotate(amount=Sum('amount'))
    )
    ingredients_list = (
        f'{ingredient["ingredients__name"]}: {ingredient["amount"]}'
        f'{ingredient["measurement"]}'
        for ingredient in ingredients
    )
    shopping_list.extend(ingredients_list)
    shopping_list.append(
        '\n Составлено в Foodgram.\n'
        'Автор - студент 26 когорты Евгений Иванов.')
    return "\n".join(shopping_list)


def incorrect_keyboard_layout(url_string: str) -> str:
    """Перевод слов, если не переключена раскладка."""
    equals = str.maketrans(
        "qwertyuiop[]asdfghjkl;'zxcvbnm,./",
        "йцукенгшщзхъфывапролджэячсмитьбю.",
    )
    if url_string.startswith('%'):
        return unquote(url_string).lower()
    return url_string.translate(equals).lower()
