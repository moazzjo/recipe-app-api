"""
Test for recipe api
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status # type: ignore
from rest_framework.test import APIClient # type: ignore

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer # type: ignore

RECIPES_URL = reverse('recipe:recipe-list')

def detail_urls(recipe_id):
    """Create and return a recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])



def create_recipe(user, **params):
    """ Create and return a sample recipe. """

    defaults = {
            'title': 'sample recipe name',
            'time_minutes' : 5,
            'price' : Decimal('1.5'),
            'description' : 'sample recipe desciription'
    }

    defaults.update(params)

    recipe = Recipe.objects.create(user = user, **defaults)

    return recipe


def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicRecipeApiTests(TestCase):
    """ Test unauthentication API requests. """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test auth is required to call API. """
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivateRecipeApiTests(TestCase):
    """ Test for authenticated API requests. """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )

        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """ Test retriving list of recipes. """
        create_recipe(user = self.user)
        create_recipe(user = self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many =True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_is_restricted_to_the_user(self):
        """ Test list of recipes is limted to the athenticated user. """
        other_user = create_user(
            email = 'other@example.com',
            password = 'pass123'
        )

        create_recipe(user = other_user)
        create_recipe(user = self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user = self.user)
        serializer = RecipeSerializer(recipes, many =True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """ test get the recipe detail """
        recipe = create_recipe(user= self.user)

        url= detail_urls(recipe.id)
        res = self.client.get(url)


        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """ Test creating recipe. """

        payload = {
            'title': 'sample recipe name',
            'time_minutes' : 5,
            'price' : Decimal('1.5'),
        }

        res= self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id = res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(recipe,key), value)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """ Test partial update of recipe. """
        origin_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user = self.user,
            title= 'simple tite of the recipe',
            link = origin_link
        )

        payload = {'title': 'new title simple of recipe'}
        url = detail_urls(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, origin_link)
        self.assertEqual(recipe.user, self.user)



    def test_full_update(self):
        """ test update all of the recipe attr. """
        recipe = create_recipe(
            user = self.user,
            title = 'sample recipe name',
            description = 'sample recipe desciription',
            link = 'https://example.com/recipe.pdf'
        )


        payload = {
            'title': 'new sample recipe name',
            'time_minutes' : 10,
            'price' : Decimal('1.5'),
            'description' : 'new sample recipe desciription'
        }

        url = detail_urls(recipe.id)
        res = self.client.put(url, payload)
        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k,v in payload.items():
            self.assertEqual(getattr(recipe,k), v) 
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """ Test changing the recipe user results in an error. """
        new_user = create_user(
            email = "test@example.com",
            password = "test123",
        )

        recipe = create_recipe(user = self.user)

        payload = {
            'user' : new_user.id
        }

        url = detail_urls(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)
    
    def test_delete_recipe(self):
        """ Test deleting a recipe successful. """
        recipe = create_recipe(
            user = self.user
        )

        url = detail_urls(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id = recipe.id).exists())

    def test_delete_recipe_for_another_user(self):
        """ Test deleting a recipe for another user not allowed. """
        another_user = create_user(
            email = 'test@example.com',
            password = 'test123',
        )

        recipe = create_recipe(
            user = another_user
        )

        url = detail_urls(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id = recipe.id).exists())

    def create_recipe_with_new_tags(self):
        """ Test creating recipe with new tags. """

        payload = {
            'title': "sample title",
            'time_minutes': 2,
            'price': Decimal('2.5'),
            'tags': [{'name': 'Thai'}, {'name': 'lam'}]
        }

        res= self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]

        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                user= self.user,
                name = tag['name']
            ).exists()

            self.assertTrue(exists)

    def create_recipe_with_existing_tag(self):
        """ Test creating a recipe with existing tag. """

        tag_indian = Tag.objects.create(user = self.user, name = 'Indian')

        payload = {
            'title': 'sample recipe name',
            'time_minutes' : 5,
            'price' : Decimal('1.5'),
            'tags': [{'name': 'Indian'}, {'name': 'Ramdan'}]       
        }
        
        res = self.client.post(RECIPES_URL, payload, format = 'json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name = tag['name'],
                user = self.user,
                
            ).exists()
            self.assertTrue(exists)



    def test_create_tag_on_update(self):
        """ Test creating tag when updating a recipe. """
        recipe = create_recipe(user = self.user)

        payload = {
            'tags': [{'name':'Lunch'}]
        }

        url = detail_urls(recipe.id)
        res = self.client.patch(url, payload, format = 'json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user = self.user, name = 'Lunch')
        self.assertIn(new_tag, recipe.tags.all())
    

    
    def test_update_recipe_assign_tag(self):
        """ Test assigning an existing tag when updating a recipe. """
        tag_breakfast = Tag.objects.create(user = self.user, name= 'BreakFast')
        recipe = create_recipe(user = self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user = self.user, name= 'Lunch')
        payload = {
            'tags': [{'name' : 'Lunch'}]
        }
        url = detail_urls(recipe.id)
        res = self.client.patch(url, payload, format = 'json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())


    def test_clear_recipe_tags(self):
        """ Test clearing a recipes tags. """

        tag = Tag.objects.create(user = self.user, name='hakona makta')
        recipe = create_recipe(user = self.user)
        recipe.tags.add(tag)

        payload = {
            'tags':[]
        }

        url = detail_urls(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)
            
    def test_create_recipe_with_ingredients(self):
        """ Test creating a rceipe  with a new ingredients. """
        payload = {
            'title': 'sample recipe name',
            'time_minutes' : 5,
            'price' : Decimal('1.5'),
            'ingredients': [{'name': 'salt'}, {'name': 'milk'}]    
        }     

        res = self.client.post(RECIPES_URL, payload, format = 'json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user= self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            exists = Ingredient.objects.filter(
                user = self.user,
                name = ingredient['name']
            ).exists()
            self.assertTrue(exists)


    def test_create_ingredient_on_update(self):
        """ Test creating an ingredient when updating a recipe"""

        recipe = create_recipe(user = self.user)

        payload = {
            'ingredients':[{'name':'limos'}]
        }

        url = detail_urls(recipe.id)
        res = self.client.patch(url, payload, format = 'json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user = self.user)
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredent(self):
        """ Test assigning an existing ingredient when updating a recipe. """
        Ingredient1 = Ingredient.objects.create(user = self.user, name = 'limos')
        recipe = create_recipe(user = self.user)
        recipe.ingredients.add(Ingredient1)


        Ingredient2 = Ingredient.objects.create(user = self.user, name = 'loka')
        payload = {
            'ingredients': [{'name':'loka'}]
                 }
        
        url = detail_urls(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(Ingredient2, recipe.ingredients.all())
        self.assertNotIn(Ingredient1, recipe.ingredients.all())


    def test_clear_recipe_ingredients(self):
        """ Test clearing a recipes ingredients. """

        ingredient = Ingredient.objects.create(user = self.user, name='makta')
        recipe = create_recipe(user = self.user)
        recipe.ingredients.add(ingredient)

        payload = {
            'ingredients':[]
        }

        url = detail_urls(recipe.id)
        res = self.client.patch(url, payload, format='json')


        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)





        


    
