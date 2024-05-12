from django.contrib import admin

from foodgram.settings import EMPTY_VALUE
from .models import(
    Tag,
    Ingredient,
    Recipe,
    IngredientInRecipe,
    Favorite,
    ShoppingList,
    ShortLink,
)
from .mixins import AdminMixin


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Администрирование для модели тэгов."""

    list_display = (
        'id',
        'name',
        'slug',
    )
    list_filter = (
        'name',
        'slug',
    )
    empty_value_display = EMPTY_VALUE


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Администрирование для модели ингредиентов."""

    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = (
        'name',
        'measurement_unit',
    )
    empty_value_display = EMPTY_VALUE


class IngredientInLine(admin.TabularInline):
    model = IngredientInRecipe
    extra = 5


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Администрирование для модели рецептов."""

    list_display = (
        'id',
        'name',
        'author',
        'text',
        'cooking_time',
        'image',
        'amount_of_favorites',
    )
    list_filter = (
        'name',
        'author',
        'tags',
    )
    empty_value_display = EMPTY_VALUE
    inlines = (IngredientInLine,)

    @admin.display(description='Количество добавлений в избранное')
    def amount_of_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Favorite)
class FavoriteAdmin(AdminMixin):
    """Администрирование для модели избранного."""

    pass


@admin.register(ShoppingList)
class ShoppingListAdmin(AdminMixin):
    """Администрование для модели списка покупок."""

    pass


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    """Администрирование для модели коротких ссылок."""

    list_display = (
        'full_url',
        'short_url',
    )
    search_fields = ('full_url', 'short_url')
