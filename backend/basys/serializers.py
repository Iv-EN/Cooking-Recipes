from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    CharField, EmailField, Field, IntegerField, ModelSerializer,
    PrimaryKeyRelatedField, ReadOnlyField, SerializerMethodField,
)
from rest_framework.validators import UniqueValidator

from recipes.models import AmountIngredient, Ingredient, Recipe, Tag
from users.models import Follow

from .utils import recipe_ingredient_create

User = get_user_model()


class CreateCustomUserSerializer(UserCreateSerializer):
    '''Сериализатор регистрации пользователей.'''
    username = CharField(
        validators=[UniqueValidator(
            queryset=User.objects.all()
        )]
    )
    email = EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all()
        )]
    )

    class Meta:
        model = User
        field = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}


class CustomUserSerializer(UserSerializer):
    '''Сериализатор пользователей.'''
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

        def get_is_subscribed(self, obj):
            user = self.context['request'].user
            if user.is_authenticated:
                return Follow.objects.filter(user=user, author=obj).exists()
            return False


class RecipeFollowFieldSerializer(Field):
    '''Сериализатор вывода рецептов из подписок.'''

    def get_attribute(self, instance):
        return Recipe.objects.filter(author=instance.author)

    def to_representation(self, value):
        recipes_data = []
        for recipes in value:
            recipes_data.append(
                {
                    'id': recipes.id,
                    'name': recipes.name,
                    'image': recipes.image.url,
                    'cooking_time': recipes.cooking_time,
                }
            )
        return recipes_data


class FollowSerializer(ModelSerializer):
    '''Сериализатор подписок.'''
    recipes = RecipeFollowFieldSerializer()
    recipes_count = SerializerMethodField(read_only=True)
    id = ReadOnlyField(source='author.id')
    email = ReadOnlyField(source='author.email')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'recipes',
            'recipes_count',
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()


class TagSerializer(ModelSerializer):
    '''Сериализатор тэгов.'''
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    '''Сериализатор ингредиентов.'''
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class CreateIngredientSerializer(ModelSerializer):
    '''Сериализатор добавления ингредиентов в рецепт.'''
    id = IntegerField()

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount')


class ReadIngredientsRecipeSerializer(ModelSerializer):
    '''Сериализатор чтения ингредиентов из рецепта.'''
    id = ReadOnlyField(source='ingredients.id')
    name = ReadOnlyField(source='ingredients.name')
    measurement_unit = ReadOnlyField(source='ingredients.measurement_unit')

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name',
                  'measurement_unit',
                  'amount',)


class RecipeSerializer(ModelSerializer):
    '''Сериализатор рецептов.'''
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    is_in_shooping_cart = SerializerMethodField()
    is_favorited = SerializerMethodField()
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('id', 'author',)

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.cart.filter(user=user).exist()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anjnymous:
            return False
        return obj.favorites.filter(user=user).exists()

    @staticmethod
    def get_ingredients(obj):
        ingredients = AmountIngredient.objects.filter(recipe=obj)
        return ReadIngredientsRecipeSerializer(ingredients, many=True).data


class CreateRecipeSerializer(ModelSerializer):
    '''Сериализатор создания рецепта.'''
    ingredients = CreateIngredientSerializer(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    image = Base64ImageField(max_length=None, use_url=True)
    name = CharField(max_length=200)
    cooking_time = IntegerField(min_value=1)
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags',
                  'image', 'name', 'text',
                  'cooking_time', 'author')
        read_only_ields = ('id', 'author', 'tags',)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = [ingredient['id'] for ingredient in ingredients]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise ValidationError(
                'Какой-то ингредиент выбран более 1 раза.'
            )
        return data

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredient_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        recipe_ingredient_create(ingredient_data, AmountIngredient, recipe)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        AmountIngredient.objects.filter(recipe=recipe).delete()
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        data = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}).data
        return data

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            raise ValidationError('Время приготовления должно быть больше 0')
        return cooking_time

    def validate_ingredients(self, ingredients):
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise ValidationError(
                    'Количество ингредиентов должно быть больше 0'
                )
        return ingredients


class RecipeForFollowersSerializer(ModelSerializer):
    '''Сериализатор вывода рецептов в избранном и списке покупок.'''
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
