from django_filters.rest_framework import (
    AllValuesMultipleFilter, BooleanFilter, FilterSet,
)
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class SearchIngredientFilter(SearchFilter):
    search_param = 'name'


class FilterRecipes(FilterSet):
    """Фильтр сортировки рецептов."""

    tags = AllValuesMultipleFilter(
        field_name='tags__slug',
        label='tags'
    )
    favorite = BooleanFilter(method='get_favorite')
    shopping_cart = BooleanFilter(method='get_shopping_cart')
    author = AllValuesMultipleFilter(
        field_name='author__id',
        label='Автор'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'favorite', 'shopping_cart')

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def get_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
