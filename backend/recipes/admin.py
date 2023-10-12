from django.contrib.admin import ModelAdmin, TabularInline, register, site
from django.contrib.auth.models import Group

from .models import (AmountIngredient, Favorites_Recipes, Ingredient, Recipe,
                     ShoppingCart, Tag)

site.unregister(Group)


class IngredientRecipeInLine(TabularInline):
    '''Вывод количества ингридиентов в рецепте.'''
    model = AmountIngredient
    extra = 2


@register(Tag, AmountIngredient)
class LinksAdmin(ModelAdmin):
    pass


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    save_on_top = True


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author',)
    list_filter = ('name', 'author__username', 'tags__name')
    save_on_top = True
    inlines = (IngredientRecipeInLine,)


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ('user', 'recipe', )
    list_filter = ('user',)
    save_on_top = True


@register(Favorites_Recipes)
class FavoritesRecipesAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('user',)
    save_on_top = True
