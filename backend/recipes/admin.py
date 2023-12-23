from typing import Any
from django.contrib.admin import (ModelAdmin, TabularInline,
                                  display, register, site)
from django.contrib.auth.models import Group
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe

from .forms import TagForm
from .models import (AmountIngredient, Basket, Favorite,
                     Ingredient, Recipe, Tag)

site.unregister(Group)
site.site_header = 'Админ-зона Foodgram'


class IngredientRecipeInLine(TabularInline):
    """Вывод количества ингридиентов в рецепте."""

    model = AmountIngredient
    extra = 2


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    save_on_top = True


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author', 'get_image', 'count_favorites',)
    fields = (
        ('name', 'cooking_time',),
        ('author', 'tags',),
        ('text', 'image'),
    )
    ram_id_fields = ('author',)
    list_filter = ('name', 'author__username')
    search_fields = ('name',)
    save_on_top = True
    inlines = (IngredientRecipeInLine,)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).select_related(
            'author'
        ).prefetch_related('ingredients', 'tags')

    def get_image(self, obj: Recipe) -> SafeString:
        return mark_safe(f'<img src={obj.image.url} width="80" hieght="30"')

    get_image.short_description = 'Изображение'

    def count_favorites(self, obj: Recipe) -> int:
        return obj.in_favorite.count()

    count_favorites.short_description = 'В избранном'


@register(Tag)
class TagAdmin(ModelAdmin):
    form = TagForm
    list_display = (
        'name',
        'slug',
        'color_code',
    )
    search_fields = ('name', 'color')
    save_on_top = True

    @display(description='Colored')
    def color_code(self, obj: Tag):
        return format_html(
            '<span style="color: #{};">{}</span', obj.color[1:], obj.color
        )
    color_code.short_description = "Код цвета тэга"


@register(Basket)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ('user', 'recipe', 'date_added')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user__username', 'recipe__name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'recipe')

    def has_change_permission(
        self, request: WSGIRequest, obj: Basket | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: WSGIRequest, obj: Basket | None = None
    ) -> bool:
        return False


@register(Favorite)
class FavoritesRecipesAdmin(ModelAdmin):
    list_display = ('user', 'recipe', 'date_added')
    search_fields = ('user__username', 'recipe__name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'recipe')

    def has_change_permission(
        self, request: WSGIRequest, obj: Favorite | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: WSGIRequest, obj: Favorite | None = None
    ) -> bool:
        return False
