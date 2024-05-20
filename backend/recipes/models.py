import random

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from foodgram.settings import (MAX_LENGTH_OF_INGREDIENT, MAX_LENGTH_OF_RECIPE,
                               MAX_LENGTH_OF_TAG, MAX_LENGTH_OF_TAG_SLUG,
                               MAX_LENGTH_OF_UNIT,
                               MESSAGE_FOR_TAG_SLUG_VALIDATOR,
                               MIN_TIME_OF_COOKING, MIN_VALUE_OF_INGREDIENTS,
                               REGEX_OF_SLUG, SHORT_LINK_LENGTH,
                               SYMBOLS_FOR_SHORT_LINK)

User = get_user_model()


class Tag(models.Model):
    """Модель тэгов для рецептов."""

    name = models.CharField(
        verbose_name='Тэг',
        max_length=MAX_LENGTH_OF_TAG,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг тэга',
        max_length=MAX_LENGTH_OF_TAG_SLUG,
        unique=True,
        validators=[
            RegexValidator(
                regex=REGEX_OF_SLUG,
                message=MESSAGE_FOR_TAG_SLUG_VALIDATOR,
            )
        ]
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для ингредиентов."""

    name = models.CharField(
        verbose_name='Название ингридиента',
        max_length=MAX_LENGTH_OF_INGREDIENT,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH_OF_UNIT,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для рецептов."""

    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='IngredientInRecipe',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipes'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/',
        default=None,
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=MAX_LENGTH_OF_RECIPE,
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                MIN_TIME_OF_COOKING,
                message=(
                    f'Минимальное время приготовления в минутах '
                    f'- {MIN_TIME_OF_COOKING}'
                )
            )
        ],
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Промежуточная модель для ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='ingredients_in_recipe',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='ingredients_in_recipe',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов в рецепте',
        validators=[
            MinValueValidator(
                MIN_VALUE_OF_INGREDIENTS,
                message=(
                    f'Минимальное количество ингредиентов '
                    f'в рецепте - {MIN_VALUE_OF_INGREDIENTS}'
                )
            )
        ],
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return f'Рецепт: {self.recipe} Ингредиент: {self.ingredient}'


class Favorite(models.Model):
    """Модель для избранных рецептов."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='favorites',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'

    def __str__(self):
        return f'Пользователь: {self.user.username} Рецепт: {self.recipe.name}'


class ShoppingList(models.Model):
    """Модель для списка покупок."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='shopping_list',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='shopping_list',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'

    def __str__(self):
        return f'Пользователь: {self.user.username} Рецепт: {self.recipe.name}'


class ShortLink(models.Model):
    """Модель для коротких ссылок."""

    full_url = models.URLField()
    short_url = models.CharField(
        max_length=SHORT_LINK_LENGTH,
        db_index=True,
        blank=True,
    )

    def save(self, *args, **kwargs):

        if not self.short_url:
            while True:
                self.short_url = ''.join(
                    random.choices(
                        SYMBOLS_FOR_SHORT_LINK,
                        k=SHORT_LINK_LENGTH,
                    )
                )
                if not ShortLink.objects.filter(
                    short_url=self.short_url
                ).exists():
                    break
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'

    def __str__(self):
        return (
            f'Полная ссылка: {self.full_url} - '
            f'Короткая ссылка: {self.short_url}'
        )
