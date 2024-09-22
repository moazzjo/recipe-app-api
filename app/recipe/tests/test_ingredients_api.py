"""
Test for Ingredient api
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status # type: ignore
from rest_framework.test import APIClient # type: ignore

from core.models import Recipe, Ingredient

from recipe.serializers import IngredientSerializer  # type: ignore

INGREDIENT_URL = reverse('recipe:ingredient-list')

def create_recipe(user, **params):
    """ Create and return a sample recipe. """

    defaults = Recipe.objects.create(

            user = user,
            title= 'sample recipe name',
            time_minutes = 5,
            price = Decimal('1.5'),
            description = 'sample recipe desciription'
        
    ) 

    
    return defaults

def create_user(email = 'test@example.com', password = 'test123'):
    """ create and return user. """
    return get_user_model().objects.create_user(email=email, password=password)


def detail_urls(ingredient_id):
    """ create and return ingredient detail url. """
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientApiTests(TestCase):
    """ Test unauthenticated API request. """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ test auth is required for retrieving Ingredient. """
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """ Test authenticated API request. """

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)


    def test_retrieve_ingredients(self):
        """ Test retrieving a list of ingredients. """
        Ingredient.objects.create(user = self.user, name = 'kale')
        Ingredient.objects.create(user = self.user, name = 'vanilla')

        res = self.client.get(INGREDIENT_URL)

        Ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(Ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """ Test list of ingredient is limited to authenticated user. """
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user = user2, name = 'Pepper')
        ingredient = Ingredient.objects.create(user = self.user, name = 'salt')


        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """ Test updating an ingredient. """
        ingredient = Ingredient.objects.create(user = self.user, name='ptato')

        payload = {'name':'tomato'}

        url = detail_urls(ingredient.id)
        res = self.client.patch(url, payload)

        ingredient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()

        self.assertEqual(ingredient.name, payload['name'])


    def test_delete_ingredient(self):
        """ test deleting ingredients ."""

        ingredient = Ingredient.objects.create(user = self.user, name= 'hkona makata')

        url = detail_urls(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user = self.user)
        self.assertFalse(ingredients.exists())


    def test_filter_ingredient_assigned_to_recipe(self):
        """ Test listing ingredients by those assigied to recipes. """
        int1= Ingredient.objects.create(user = self.user, name='x1')
        int2= Ingredient.objects.create(user = self.user, name='x2')

        recipe = create_recipe(user = self.user)
        recipe.ingredients.add(int1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})


        s1 = IngredientSerializer(int1)
        s2 = IngredientSerializer(int2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)


    def test_filterd_by_ingredients_unique(self):
        """ Test filtered ingredient return unique list """

        int1= Ingredient.objects.create(user = self.user, name='eggs')
        Ingredient.objects.create(user = self.user, name='x2')

        recipe1 = create_recipe(user = self.user, title = 'eggs fries')
        recipe2 = create_recipe(user = self.user, title = 'eggs blowed')

        recipe1.ingredients.add(int1)
        recipe2.ingredients.add(int1)


        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})



        self.assertEqual(len(res.data), 1)
   



