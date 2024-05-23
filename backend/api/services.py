from django.shortcuts import get_object_or_404
from recipes.models import ShortLink


def get_full_url(short_url):
    """Функция получения полной ссылки на рецепт."""

    url = get_object_or_404(ShortLink, short_url=short_url)

    return url.full_url
