#isort: skip_file
from django.contrib.auth.hashers import make_password
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingList, ShortLink, Tag)
from .services import Base64ImageField
from users.models import Follow, User


class BaseUserSerializer(UserSerializer):
    """Базовый сериалайзер для модели пользователей."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'password',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(
                user=user,
                author=obj,
            ).exists()
        return False

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Данный email уже занят другим пользователем.'
            )
        return value


class CustomUserSerializer(BaseUserSerializer):
    """Сериалайзер для модели пользователей."""

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'POST':
            response.pop('avatar', None)
            response.pop('is_subscribed', None)
        if request and request.method == 'PUT':
            response.pop('email', None)
            response.pop('id', None)
            response.pop('username', None)
            response.pop('first_name', None)
            response.pop('last_name', None)
            response.pop('is_subscribed', None)
        return response


class FollowAndShoppingListSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления рецепта в подписки и список покупок."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели подписок."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def __init__(self, *args, is_subscribed=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_subscribed = is_subscribed

    def get_avatar(self, obj):
        return self.context['request'].build_absolute_uri(
            obj.author.avatar
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated and isinstance(obj, User):
            return Follow.objects.filter(
                user=user,
                author=obj,
            ).exists()
        return False

    def get_recipes(self, obj):
        user = obj.user
        if user.is_authenticated:
            queryset = user.recipes.all()
            limit = self.context.get(
                'request'
            ).query_params.get('recipes_limit')
            if limit:
                queryset = queryset[:int(limit)]
            return FollowAndShoppingListSerializer(
                queryset,
                many=True,
            ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели тэгов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.ReadOnlyField()

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class CreateIngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания ингредиента в рецепте."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'amount',
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериалайзер для получения рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = BaseUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredients_in_recipe',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def _get_item(self, obj, model):
        user = self.context.get('request').user
        if user.is_authenticated:
            return model.objects.filter(
                user=user,
                recipe=obj,
            ).exists()
        return False

    def get_is_favorited(self, obj):
        return self._get_item(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self._get_item(obj, ShoppingList)


class RecipeCUDSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания, удаления и редактирования рецептов."""

    ingredients = CreateIngredientInRecipeSerializer(many=True)
    author = BaseUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def _get_item(self, obj, model):
        user = self.context.get('request').user
        if user.is_authenticated:
            return model.objects.filter(
                user=user,
                recipe=obj,
            ).exists()
        return False

    def get_is_favorited(self, obj):
        return self._get_item(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self._get_item(obj, ShoppingList)

    def _set_ingredients_and_tags(self, ingredients, tags, recipe):
        recipe.tags.set(tags)
        ingredients_in_recipe = []
        for ingredient in ingredients:
            ingredients_in_recipe.append(
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient=Ingredient.objects.get(
                        id=ingredient.get('id')
                    ),
                    amount=ingredient.get('amount'),
                )
            )
        IngredientInRecipe.objects.bulk_create(ingredients_in_recipe)
        return recipe

    def validate_ingredients(self, data):
        if not data:
            raise ValidationError('Не добавлен ингредиент(ы).')
        ingredients = set()
        for ingredient in data:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            if not amount or amount < 1:
                raise ValidationError(
                    f'Количество игредиента {ingredient_id}'
                    f'меньше 1.'
                )
            ingredients.add(ingredient_id)

        if len(ingredients) != len(data):
            raise ValidationError(
                'Нельзя добавлять одинаковые ингредиенты в рецепт.'
            )

        available_ingredients = Ingredient.objects.filter(pk__in=ingredients)
        if len(available_ingredients) != len(ingredients):
            raise ValidationError(
                'Игредиент(ы) отсутствует(ют) в базе данных.'
            )
        return data

    def validate_tags(self, data):
        if not data:
            raise ValidationError(
                'Добавьте тэг к рецепту.'
            )
        tags = set(data)
        if len(data) != len(tags):
            raise ValidationError(
                'Нельзя добавлять одинаковые тэги.'
            )

        available_tags = Tag.objects.filter(
            pk__in=[tag.id for tag in data]
        )
        if len(data) != len(available_tags):
            raise ValidationError(
                'Нужно добавить хотя бы 1 тэг.'
            )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        return self._set_ingredients_and_tags(
            ingredients,
            tags,
            recipe,
        )

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        self.validate_ingredients(ingredients)
        tags = validated_data.pop('tags', [])
        self.validate_tags(tags)
        instance.ingredients.clear()
        instance.tags.clear()
        super().update(instance, validated_data)
        recipe = Recipe.objects.get(name=instance.name)
        return self._set_ingredients_and_tags(
            ingredients,
            tags,
            recipe,
        )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context=self.context).data


class ShortLinkSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели коротких ссылок."""

    class Meta:
        model = ShortLink
        fields = '__all__'

    def create(self, validated_data):
        full_url = validated_data['full_url']
        short_url, _ = ShortLink.objects.get_or_create(
            full_url=full_url,
        )
        return short_url

    def to_representation(self, instance):
        return {'short-link': instance}
