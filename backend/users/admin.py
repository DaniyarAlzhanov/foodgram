#isort: skip_file

from django.contrib import admin
from foodgram.settings import EMPTY_VALUE

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Администрирование для модели пользователей."""

    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
    )
    list_filter = (
        'email',
        'username',
    )
    search_fields = (
        'email',
        'username',
    )
    empty_value_display = EMPTY_VALUE


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Администрирование для модели подписок."""

    list_display = (
        'author',
        'user',
    )
    list_filter = (
        'author',
        'user',
    )
    search_fields = (
        'author',
        'user',
    )
    empty_value_display = EMPTY_VALUE
