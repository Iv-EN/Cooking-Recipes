from django.db.models import Count, Q, QuerySet
from django.db.models import Q, QuerySet
from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponse
from djoser.views import UserViewSet as UserViewSetDjoser
from rest_framework.decorators import action
from rest_framework.permissions import (
    DjangoModelPermissions, IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .mixins import AddDelViewMixin
from .paginations import LimitPagePagination
from .permission import AuthorOrReadOnly, AdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerialiser,
                          RecipeShortSerializer, TagSerializer,
                          UserSubscribeSerializer,)
from core.utilities import create_shoping_list, incorrect_keyboard_layout
from recipes.models import (Favorite, Ingredient, Recipe,
                            Basket, Tag)
from users.models import Subscriptions

User = get_user_model()


class BaseApiRootView(APIRootView):
    """Базовые пути API."""


class UserViewSet(UserViewSetDjoser, AddDelViewMixin):
    """Вьюсет для пользователей."""

    pagination_class = LimitPagePagination
    permission_classes = (DjangoModelPermissions,)
    add_serializer = UserSubscribeSerializer
    link_model = Subscriptions

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request: WSGIRequest, id: int | str) -> Response:
        """Создание/удаление связи между пользователями."""

    @subscribe.mapping.post
    def create_subscribe(
        self, request: WSGIRequest, id: int | str
    ) -> Response:
        return self._create_relation(Subscriptions, id)

    @subscribe.mapping.delete
    def delete_subscribe(
        self, request: WSGIRequest, id: int | str
    ) -> Response:
        return self._delete_relation(Subscriptions, Q(author__id=id))

    @action(
        methods=('get',), detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request: WSGIRequest) -> Response:
        """Список подписок пользователя."""
        pages = self.paginate_queryset(
            User.objects.filter(subscribers__user=self.request.user)
        )
        serialiser = UserSubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serialiser.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)

    def get_queryset(self) -> list[Ingredient]:
        name: str = self.request.query_params.get('name', '').strip()
        if not name:
            return self.queryset
        name = incorrect_keyboard_layout(name)
        return self.queryset.filter(name__icontains=name)


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    """Вьюсет для рецептов."""

    serializer_class = RecipeSerialiser
    pagination_class = LimitPagePagination
    permission_classes = (AuthorOrReadOnly,)
    add_serializer = RecipeShortSerializer

    def get_queryset(self) -> QuerySet[Recipe]:
        """Получение списка запрошенных объектов."""
        queryset = Recipe.objects.select_related('author').prefetch_related(
            'ingredient__ingredients', 'tags'
        )
        tags: list = self. request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author: str = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        if self.request.user.is_authenticated:
            is_in_cart: str = self.request.query_params.get(
                'is_in_shopping_cart')
            if is_in_cart in ('1', 'true'):
                queryset = queryset.filter(in_basket__user=self.request.user)
            if is_in_cart in ('0', 'false'):
                queryset = queryset.exclude(in_basket__user=self.request.user)

            is_favorite: str = self.request.query_params.get('is_favorited')
            if is_favorite in ('1', 'true'):
                queryset = queryset.filter(in_favorite__user=self.request.user)
            if is_favorite in ('0', 'false'):
                queryset = queryset.exclude(
                    in_favorite__user=self.request.user)

        return queryset

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request: WSGIRequest, pk: int | str) -> Response:
        """Добавление/удаление рецепта в избранное."""

    @favorite.mapping.post
    def recipe_to_favortes(
        self, requerest: WSGIRequest, pk: int | str
    ) -> Response:
        self.link_model = Favorite
        return self._create_relation(pk)

    @favorite.mapping.delete
    def remove_recipe_from_favorites(
        self, request: WSGIRequest, pk: int | str
    ) -> Response:
        self.link_model = Favorite
        return self._delete_relation(Q(recipe__id=pk))

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request: WSGIRequest, pk: int | str) -> Response:
        """Добавление/удаление рецепта в список покупок."""

    @shopping_cart.mapping.post
    def recipe_to_cart(self, request: WSGIRequest, pk: int | str) -> Response:
        self.link_model = Basket
        return self._create_relation(pk)

    @shopping_cart.mapping.delete
    def remove_recipe_from_cart(
        self, request: WSGIRequest, pk: int | str
    ) -> Response:
        self.link_model = Basket
        return self._delete_relation(Q(recipe__id=pk))

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request: WSGIRequest) -> Response:
        """Создание файла *.txt со списком покупок."""
        user = self.request.user
        if not user.basket.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        filename = f'{user.username}_shopping_list.txt'
        shopping_list = create_shoping_list(user)
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Cotent-Disposition'] = f'attachment; filename={filename}'
        return response


User = get_user_model()


class BaseApiRootView(APIRootView):
    """Базовые пути API."""


class UserViewSet(UserViewSetDjoser, AddDelViewMixin):
    """Вьюсет для пользователей."""

    pagination_class = LimitPagePagination
    permission_classes = (DjangoModelPermissions,)
    add_serializer = UserSubscribeSerializer
    link_model = Subscriptions

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request: WSGIRequest, id: int | str) -> Response:
        """Создание/удаление связи между пользователями."""

    @subscribe.mapping.post
    def create_subscribe(
        self, request: WSGIRequest, id: int | str
    ) -> Response:
        return self._create_relation(Subscriptions, id)

    @subscribe.mapping.delete
    def delete_subscribe(
        self, request: WSGIRequest, id: int | str
    ) -> Response:
        return self._delete_relation(Subscriptions, Q(author__id=id))

    @action(
        methods=('get',), detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request: WSGIRequest) -> Response:
        """Список подписок пользователя."""
        annotated_queryset = User.objects.filter(
            subscribers__user=request.user
        ).annotate(recipes_count=Count('recipes'))
        pages = self.paginate_queryset(annotated_queryset)
        serialiser = UserSubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serialiser.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)

    def get_queryset(self) -> list[Ingredient]:
        name: str = self.request.query_params.get('name').strip()
        if name:
            return self.queryset.filter(name__icontains=name)
        return self.queryset


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    """Вьюсет для рецептов."""

    serializer_class = RecipeSerialiser
    pagination_class = LimitPagePagination
    permission_classes = (AuthorOrReadOnly,)
    add_serializer = RecipeShortSerializer

    def get_queryset(self) -> QuerySet[Recipe]:
        """Получение списка запрошенных объектов."""
        queryset = Recipe.objects.select_related('author').prefetch_related(
            'ingredient__ingredients', 'tags'
        )
        tags: list = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author: str = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        if self.request.user.is_authenticated:
            is_in_cart: str = self.request.query_params.get(
                'is_in_shopping_cart')
            if is_in_cart in ('1', 'true'):
                queryset = queryset.filter(in_basket__user=self.request.user)
            elif is_in_cart in ('0', 'false'):
                queryset = queryset.exclude(in_basket__user=self.request.user)

            is_favorite: str = self.request.query_params.get('is_favorited')
            if is_favorite in ('1', 'true'):
                queryset = queryset.filter(in_favorite__user=self.request.user)
            elif is_favorite in ('0', 'false'):
                queryset = queryset.exclude(
                    in_favorite__user=self.request.user)

        return queryset

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request: WSGIRequest, pk: int | str) -> Response:
        """Добавление/удаление рецепта в избранное."""
    @favorite.mapping.post
    def recipe_to_favorites(
        self, requerest: WSGIRequest, pk: int | str
    ) -> Response:
        return self._create_relation(Favorite, pk)

    @favorite.mapping.delete
    def remove_recipe_from_favorites(
        self, request: WSGIRequest, pk: int | str
    ) -> Response:
        return self._delete_relation(Favorite, Q(recipe__id=pk))

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request: WSGIRequest, pk: int | str) -> Response:
        """Добавление/удаление рецепта в список покупок."""
    @shopping_cart.mapping.post
    def recipe_to_cart(self, request: WSGIRequest, pk: int | str) -> Response:
        return self._create_relation(Basket, pk)

    @shopping_cart.mapping.delete
    def remove_recipe_from_cart(
        self, request: WSGIRequest, pk: int | str
    ) -> Response:
        return self._delete_relation(Basket, Q(recipe__id=pk))

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request: WSGIRequest) -> Response:
        """Создание файла *.txt со списком покупок."""
        user = self.request.user
        if not user.basket.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        filename = f'{user.username}_shopping_list.txt'
        shopping_list = create_shoping_list(user)
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Cotent-Disposition'] = f'attachment; filename={filename}'
        return response
