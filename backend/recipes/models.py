from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Length
from PIL import Image

from core.validators import ColorValidator, ValidateName

User = get_user_model()

models.CharField.register_lookup(Length)


class Tag(models.Model):
    """Тэги для рецептов."""

    name = models.CharField(
        verbose_name='Тэг',
        max_length=settings.MAX_LEN_RECIPES_CHARFIELD,
        validators=[ValidateName(field='Название тэга'), ],
        unique=True
    )
    color = models.CharField(
        verbose_name='Цвет в НЕХ',
        max_length=7,
        unique=True,
        db_index=False,
        default='#FF0000'
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

    def __str__(self) -> str:
        return f'{self.name} (цвет: {self.color})'

    def clean(self) -> None:
        self.name = self.name.strip().lower()
        self.slug = self.slug.strip().lower()
        color_validator = ColorValidator()
        self.color = color_validator.validate(self.color)
        return super().clean()


class Ingredient(models.Model):
    """Ингредиенты для рецепта."""

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
                name='unique_for_ingredient',
            ),
            models.CheckConstraint(
                check=models.Q(measurement_unit__length__gt=0),
                name='%(app_label)s_%(class)s_measurement_unit is empty',
            ),
        )

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'

    def clean(self) -> None:
        self.name = self.name.lower()
        self.measurement_unit = self.measurement_unit.lower()
        super().clean()


class Recipe(models.Model):
    """Основная модель рецептов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=settings.MAX_LEN_RECIPES_CHARFIELD,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE,
        null=True,
    )
    tags = models.ManyToManyField(
        'Tag',
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
    )
    text = models.TextField(
        verbose_name='Описание блюда',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин',
        default=0,
        validators=(
            MinValueValidator(
                settings.MIN_COOKING_TIME,
                message=f'Не менее {settings.MIN_COOKING_TIME} мин.'
            ),
            MaxValueValidator(
                settings.MAX_COOKING_TIME,
                message=(
                    f'Более {settings.MAX_COOKING_TIME} мин - слишком долго'
                )
            )
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
                name='%(app_label)s_%(class)s_name is empty',
            ),
        )

    def __str__(self) -> str:
        return f'{self.name}. Автор: {self.author}'

    def clean(self) -> None:
        self.name = self.name.capitalize()
        return super().clean()

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        image = Image.open(self.image.path)
        image.thumbnail((500, 500))
        image.save(self.image.path)


class AmountIngredient(models.Model):
    """Количество ингредиентов."""

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
        validators=(
            MinValueValidator(
                settings.MIN_AMOUNT_INGREDIENTS,
                message=f'Не менее {settings.MIN_AMOUNT_INGREDIENTS}'
            ),
            MaxValueValidator(
                settings.MAX_AMOUNT_INGREDIENTS,
                message='Слишком много!'
            )
        ),
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'recipe',
                    'ingredients',
                ),
                name='%(app_label)s_%(class)s ingredient alredy added',
            ),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'


class Favorite(models.Model):
    """Избранные рецепты."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт из избранного',
        related_name='in_favorite',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Автор избранного',
        related_name='favorite',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='\n%(app_label)s_%(class)s recipe is favorite already\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.recipe} в избранном у {self.user}'


class Basket(models.Model):
    """Список покупок."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты из списка покупок',
        related_name='in_basket',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Список покупок пользователя',
        related_name='basket',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(app_label)s_%(class)s recipe is list already',
            ),
        )

    def __str__(self) -> str:
        return f'{self.recipe} в списке покупок у {self.user}'
