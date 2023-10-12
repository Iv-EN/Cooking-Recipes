from django_filters.rest_framework import (
    AllValuesMultipleFilter, BooleanFilter, FilterSet, ModelChoiceFilter,
)
from rest_framework.filters import SearchFilter

from recipes.models import Recipe
from users.models import CustomUser


class SearchIngredientFilter(SearchFilter):
    search_param = 'name'


class FilterRecipes(FilterSet):
    '''Фильтр сортировки рецептов.'''
    tags = AllValuesMultipleFilter(field_name='tags__slug',
                                   label='tags')
    favorite = BooleanFilter(method='get_favorite')
    shopping_cart = BooleanFilter(methid='get_shopping_cart')
    author = ModelChoiceFilter(queryset=CustomUser.objects.all())

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'favorite', 'shopping_cart')

    def get_favorite(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def get_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class FilterIngredientSearch(SearchFilter):
    search_param = 'name'
