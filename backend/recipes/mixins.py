from django.contrib import admin

from foodgram.settings import EMPTY_VALUE


class AdminMixin(admin.ModelAdmin):
    """Миксин для класса администрирования."""

    list_display = (
        'user',
        'recipe',
    )
    empty_value_display = EMPTY_VALUE
