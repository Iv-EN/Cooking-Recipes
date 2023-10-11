from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.models import (
    AmountIngredient, Favorites_Recipes, Ingredient, Recipe, ShoppingCart, Tag,
)
from users.models import CustomUser, Follow

from .filters import FilterRecipes, SearchIngredientFilter
from .paginations import LimitPagePagination
from .permission import IsAdminOrAuthor, IsAdminOrReadOnly
from .serializers import (
    CreateRecipeSerializer, CustomUserSerializer, FollowSerializer,
    IngredientSerializer, RecipeForFollowersSerializer, RecipeSerializer,
    TagSerializer,
)


class UserViewSet(UserViewSet):
    '''Вьюсет для модели пользователей.'''
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = LimitPagePagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    permission_classes = (AllowAny,)

    def subscribed(self, serializer, id=None):
        follower = get_object_or_404(CustomUser, id=id)
        if self.request.user == follower:
            return Response(
                {'message': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow = Follow.objects.get_or_create(
            user=self.request.user, author=follower)
        serializer = FollowSerializer(follow[0])
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def unsubscribed(self, serializer, id=None):
        follower = get_object_or_404(CustomUser, id=id)
        Follow.objects.filter(user=self.request.user, author=follower).delete()
        return Response(
            {'message': 'Вы успешно отписались'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, serialiser, id):
        if self.request.method == 'DELETE':
            return self.unsubscribed(serialiser, id)
        return self.subscribed(serialiser, id)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, serializer):
        following = Follow.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(following)
        serializer = FollowSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(ModelViewSet):
    '''Вьюсет для тэгов.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ModelViewSet):
    '''Вьюсет для ингредиентов.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    filter_backends = (SearchIngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    '''Вьюсет для рецептов.'''
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthor,)
    pagination_class = LimitPagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterRecipes

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeSerializer
        if self.action == 'retrieve':
            return RecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            Favorites_Recipes.objects.create(user=request.user,
                                             recipe=recipe)
            serializer = RecipeForFollowersSerializer(recipe)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        deleted = get_object_or_404(
            Favorites_Recipes,
            user=request.user,
            recipe=recipe
        )
        deleted.delete()
        return Response({'message': 'Рецепт успешно удалён из избранного'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            ShoppingCart.objects.create(user=request.user,
                                        recipe=recipe)
            serializer = RecipeForFollowersSerializer(recipe)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        deleted = get_object_or_404(ShoppingCart,
                                    user=request.user,
                                    recipe=recipe)
        deleted.delete()
        return Response({'message': 'Рецепт успешно удалён из списка покупок'},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = AmountIngredient.objects.filter(
            recipe_shopping_cart_user=user).values(
                'ingredients__name',
                'ingredients__measurement_unit').annotate(amount=Sum('amount'))
        data = ingredients.values_list(
            'ingredients__name',
            'ingredients__measurement_unit',
            'amount'
        )
        shopping_cart = 'Список покупок:\n'
        for name, measure, amount in data:
            shopping_cart += (f'{name.capitalize()} {amount} {measure}, \n')
        response = HttpResponse(shopping_cart, content_type='text/plain')
        return response
