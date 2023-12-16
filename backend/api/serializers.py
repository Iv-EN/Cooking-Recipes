from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import F, QuerySet
from django.db.transaction import atomic
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import ModelSerializer, IntegerField, SerializerMethodField

from core.validators import IngredientsValidator, TagsValidator
from core.utilities import recipe_ingredients_set
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class RecipeShortSerializer(ModelSerializer):
    """Сериализатор для модели Recipe."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
        read_only_fields = fields


class UserSerializer(ModelSerializer):
    """Сериализатор для модели CustomUser."""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj: User) -> bool:
        """Проверка подписок."""
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.subscriptions.filter(author=obj).exists()

    def create(self, validated_data: dict) -> User:
        """Создание нового пользователя."""
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSubscribeSerializer(UserSerializer):
    """Сериализатор вывода подписок текущего пользователя."""

    recipes = RecipeShortSerializer(many=True, read_only=True)
    recipes_count = IntegerField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj: User) -> bool:
        """Проверка наличия подписок."""
        return True


class TagSerializer(ModelSerializer):
    '''Сериализатор вывода тэгов.'''

    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug',
        )
        read_only_fields = fields

    def validate(self, attrs: OrderedDict) -> OrderedDict:
        """Унификация вводных данных тэга."""
        for attr, value in attrs.items():
            attrs[attr] = value.sttrip(' #').upper()
        return attrs


class IngredientSerializer(ModelSerializer):
    """Сериализатор вывода ингридиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only_fields = fields


class RecipeSerialiser(ModelSerializer):
    """Сериализатор рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )
        read_only_fields = ('is_favorited', 'is_in_shopping_cart',)

    def get_ingredients(self, recipe: Recipe) -> QuerySet[dict]:
        """Получение списка ингредиентов для рецепта."""
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F(
                'ingredient_recipes__amount'
            )
        )
        return ingredients

    def get_is_favorited(self, recipe: Recipe) -> bool:
        """Проверка нахождения рецепта в избранных."""
        user = self.context.get('view').request.user
        if user.is_anonymous:
            return False
        return user.favorite.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
        """Проверка нахождения рецепта в списке покупок."""
        user = self.context.get('view').request.user
        if user.is_anonymous:
            return False
        return user.basket.filter(recipe=recipe).exists()

    def validate(self, data: OrderedDict) -> OrderedDict:
        """Проверка данных при создании/редактировании рецепта."""
        tags_id: list[int] = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        if not tags_id or not ingredients:
            raise ValidationError('Не хватает данных')
        tags_validator = TagsValidator()
        tags = tags_validator.validate(tags_id, Tag)
        ingredients = IngredientsValidator.validate(ingredients, Ingredient)
        data.update(
            {'tags': tags, 'ingredients': ingredients,
             'author': self.context.get('request').user, }
        )
        return data

    @atomic
    def create(self, validated_data: dict) -> Recipe:
        """Создание рецепта."""
        tags: list[int] = validated_data.pop('tags')
        ingredients: dict[int, tuple] = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe_ingredients_set(recipe, ingredients)
        return recipe

    @atomic
    def update(self, intance: Recipe, validated_data: dict):
        """Изменение рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().update(intance, validated_data)
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            recipe_ingredients_set(recipe, ingredients)
        recipe.save()
        return recipe
