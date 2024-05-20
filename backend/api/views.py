# isort: skip_file

from io import BytesIO
from urllib.parse import urlparse

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPaginator
from .permissions import IsAuthorOrAdmin
from recipes.models import (Favorite, Ingredient,
                            IngredientInRecipe, Recipe, ShoppingList, Tag)
from .serializers import (CustomUserSerializer,
                          FollowAndShoppingListSerializer, FollowSerializer,
                          IngredientSerializer, RecipeCUDSerializer,
                          RecipeGetSerializer, ShortLinkSerializer,
                          TagSerializer)
from users.models import Follow, User


class CustomUserViewSet(UserViewSet):
    """Вьюсет для роута users."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitPaginator
    filter_backends = (SearchFilter,)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = CustomUserSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        url_path='me/avatar',
        url_name='me-avatar',
        methods=('put', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def avatar(self, request):
        if request.method == 'PUT':
            if not request.data:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = CustomUserSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request},
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            user = User.objects.get(username=request.user.username)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, pk=self.kwargs.get('id'))
        existing_follow = Follow.objects.filter(
            author=author,
            user=user,
        ).exists()
        if user == author:
            return Response(
                {'errors': 'Подписаться на себя нельзя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if existing_follow:
            return Response(
                {'errors': 'Вы уже подписаны на данного автора.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow, _ = Follow.objects.get_or_create(
            user=user, author=author
        )
        serializer = FollowSerializer(
            follow,
            context={'request': request},
            is_subscribed=True,
        )
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(
            User,
            pk=self.kwargs.get('id'),
        )
        existing_follow = Follow.objects.filter(
            author=author,
            user=user,
        ).exists()

        if not existing_follow:
            return Response(
                {'errors': 'Вы не подписаны на данного автора.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Follow.objects.get(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        followings = Follow.objects.filter(user=self.request.user)
        pagination = self.paginate_queryset(followings)
        serializer = FollowSerializer(
            pagination,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для роута tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для роута ingredients."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет для роута recipes."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdmin,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPaginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCUDSerializer

    def post_delete_to_list(self, request, pk, model):
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'Такого рецепта нет в базе данных.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = FollowAndShoppingListSerializer(recipe)
            if model.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в список покупок.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            model.objects.create(
                user=request.user,
                recipe=recipe,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            try:
                recipe = Recipe.objects.get(id=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'Такого рецепта нет в базе данных.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            existing_recipe = model.objects.filter(
                user=request.user,
                recipe=recipe,
            ).exists()
            if not existing_recipe:
                return Response(
                    {'Такой рецепт отсутствует.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            model.objects.filter(
                user=request.user,
                recipe=recipe,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        return self.post_delete_to_list(
            request,
            pk,
            Favorite,
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        return self.post_delete_to_list(
            request,
            pk,
            ShoppingList,
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        buffer = BytesIO()
        pdf_file = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont(
            'FreeSans', '/app/api/fonts/FreeSans.ttf')
        )
        pdf_file.setFont('FreeSans', 15)
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_list__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(amount_of_ingredients=Sum('amount'))

        pdf_file.drawString(100, 750, 'Ваш список покупок')

        y = 700
        for ingredient in ingredients:
            pdf_file.drawString(
                100,
                y,
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["amount_of_ingredients"]} '
                f'{ingredient["ingredient__measurement_unit"]}',
            )
            y -= 20

        pdf_file.showPage()
        pdf_file.save()
        buffer.seek(0)
        response = FileResponse(
            buffer,
            as_attachment=True,
            filename='shopping_list.pdf'
        )
        return response

    @action(
        detail=True,
        url_path='get-link',
        url_name='get-link',
        methods=('get',),
        permission_classes=(AllowAny,),
    )
    def short_link(self, request, pk):
        full_url = request.build_absolute_uri().rstrip('get-link/')
        serializer = ShortLinkSerializer(
            data={'full_url': full_url}
        )
        if serializer.is_valid(raise_exception=True):
            url = serializer.create(
                validated_data=serializer.validated_data
            )
            parse_url = urlparse(full_url)
            base_url = parse_url.scheme + '://' + parse_url.netloc + '/s/'
            short_url = base_url + url.short_url
            return Response(
                {'short-link': short_url}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            return serializer.save(author=self.request.user)
        else:
            raise NotAuthenticated()

    def perform_update(self, serializer):
        if self.request.user.is_authenticated:
            return serializer.save(author=self.request.user)
        else:
            raise NotAuthenticated()
