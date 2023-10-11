from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Length

from basys.validators import validate_name, color_validator

User = get_user_model()

models.CharField.register_lookup(Length)


class Tag(models.Model):
    '''Тэги для рецептов.'''
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.MAX_LEN_RECIPES_CHARFIELD,
        validators=(validate_name,),
        unique=True
    )
    color = models.CharField(
        verbose_name='Цвет в НЕХ',
        max_length=7,
        unique=True,
        db_index=False
    )
    slug = models.SlugField(
        verbose_name='Идентификатор тэга',
        max_length=settings.MAX_LEN_RECIPES_CHARFIELD,
        unique=True,
        db_index=False,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'color', 'slug'],
                                    name='unique_tag')
        ]

    def __str__(self) -> str:
        return f'{self.name} (цвет: {self.color})'

    def clean(self) -> None:
        self.name = self.name.strip().lower()
        self.slug = self.slug.strip().lower()
        self.color = color_validator(self.color)
        return super().clean()


class Ingredient(models.Model):
    '''Ингредиенты для рецепта.'''
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=settings.MAX_LEN_RECIPES_CHARFIELD,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=settings.MAX_LEN_RECIPES_CHARFIELD,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            ),
            models.CheckConstraint(
                check=models.Q(name__length__gt=0),
                name='\n%(app_label)s_%(class)s_name is empty\n',
            ),
            models.CheckConstraint(
                check=models.Q(measurement_unit__length__gt=0),
                name='\n%(app_label)s_%(class)s_measurement_unit is empty\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'

    def clean(self) -> None:
        self.name = self.name.lower()
        self.measurement_unit = self.measurement_unit.lower()
        return super().clean()


class Recipe(models.Model):
    '''Основная модель рецептов.'''
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.MAX_LEN_RECIPES_CHARFIELD,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='recipes.AmountIngredient'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipe_images/',
    )
    text = models.TextField(
        verbose_name='Описание блюда',
        max_length=1000,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        validators=(
            MinValueValidator(
                settings.MIN_COOKING_TIME,
                message=f'Не менее {settings.MIN_COOKING_TIME} мин.'
            ),
        ),
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author',
            ),
            models.CheckConstraint(
                check=models.Q(name__length__gt=0),
                name='\n%(app_label)s_%(class)s_name is empty\n'
            ),
        )

    def __str__(self) -> str:
        return f'{self.name}. Автор: {self.author.get_username}'

    def clean(self) -> None:
        self.name.capitalize()
        return super().clean()


class AmountIngredient(models.Model):
    '''Количество ингредиентов.'''
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='ingredient',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='ingredient_recipes',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
        validators=(
            MinValueValidator(
                settings.MIN_AMOUNT_INGREDIENTS,
                message=f'Не менее {settings.MIN_AMOUNT_INGREDIENTS}'
            ),
        ),
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'recipe',
                    'ingredients',
                ),
                name='\n%(app_label)s_%(class)s ingredient already added\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'


class Favorites_Recipes(models.Model):
    '''Избранные рецепты.'''
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='in_favorites',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='favorites',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='\n%(app_label)s_%(class)s recipe is favorite alredy\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.recipe} в избранном у {self.user.get_username}'


class ShoppingCart(models.Model):
    '''Список покупок.'''
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='shopcarts',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты',
        related_name='shopcarts',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='\n%(app_label)s_%(class)s recipe is cart alredy\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.recipe} в списке покупок у {self.user.get_username}'
