import base64

from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import ShortLink


class Base64ImageField(serializers.ImageField):
    """Кастомное поле base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            extension = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name='image.' + extension
            )
        return super().to_internal_value(data)


def get_full_url(short_url):
    """Функция получения полной ссылки на рецепт."""

    try:
        url = ShortLink.objects.get(short_url__exact=short_url)

    except ShortLink.DoesNotExist:
        raise KeyError('Такого роута не существует.')

    return url.full_url


def redirection(request, short_url):
    """Функция перенаправления с короткой ссылки."""

    try:
        full_link = get_full_url(short_url)
        return redirect(full_link)

    except Exception as error:
        return HttpResponse(error.args)