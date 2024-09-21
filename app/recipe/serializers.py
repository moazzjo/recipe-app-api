"""
 Serializer for recipe APIs. 
"""

from rest_framework import serializers # type: ignore
from core.models import Recipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """ Seriallizer fot ingredient. """

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """ Serializer for tag. """

    class Meta:
        model= Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    """ Serializer for recipe. """
    tags = TagSerializer(many=True, required = False)
    ingredients = IngredientSerializer(many=True, required = False)


    class Meta:
        model = Recipe
        fields = [
                'id', 'title', 'time_minutes', 'price', 'link', 'tags', 
                'ingredients',
                 ]
        read_only_fields = ['id']


    def _get_tag_or_create(self, tags, recipe):
        """ handle getting or creating tags as needed. """
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user = auth_user,
                **tag
            )

            recipe.tags.add(tag_obj)


    def _get_Ingredient_or_create(self, ingredients, recipe):
        """ handle getting or creating ingredients as needed. """
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user = auth_user,
                **ingredient
            )

            recipe.ingredients.add(ingredient_obj)



    def create(self, validated_data):
        """ create a recipe override. """
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_tag_or_create(tags, recipe)
        self._get_Ingredient_or_create(ingredients, recipe)
        return recipe
    

    def update(self, instance, validated_data):
        """ update a recipe override. """
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_Ingredient_or_create(ingredients, instance)

        if tags is not None:
            instance.tags.clear()
            self._get_tag_or_create(tags, instance)


        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
      





class RecipeDetailSerializer(RecipeSerializer):
    """ serializer for recipe detail view. """

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
        




        