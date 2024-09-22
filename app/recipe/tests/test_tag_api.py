"""
 Test for tag api
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase

from core.models import Tag, Recipe

from rest_framework import status # type: ignore
from rest_framework.test import APIClient #type: ignore

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


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

def create_user(email= 'user@example.com', password= 'test1233'):
    """ Create and return user. """
    return get_user_model().objects.create_user(email=email, password=password)



class publicTagsApiTest(TestCase):
    """ Test unauthentiated api requests. """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test auth is required to retrieve tags. """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class privateTagsApiTest(TestCase):
    """ Test authenticated api requests. """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """ Test retrieve a list of tags. """

        Tag.objects.create(user = self.user, name = "Vegan")
        Tag.objects.create(user = self.user, name = "Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ test list of tags is limited to user. """
        user2 = create_user(email='example@test.com', password='test123')

        Tag.objects.create(user = user2, name="fruity")
        tag = Tag.objects.create(user=self.user, name="comfort food")

        res = self.client.get(TAGS_URL)


        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)       
        self.assertEqual(res.data[0]['name'],tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """ test updating the tag """
        tag = Tag.objects.create(user= self.user, name= 'dinner')

        payload = {
            'name' : 'before lunch'
        }
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """ Test deleting a tag """

        tag = Tag.objects.create(user=self.user, name='breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user = self.user)
        self.assertFalse(tags.exists())


    def test_filter_Tags_assigned_to_recipe(self):
        """ Test listing Tags by those assigied to recipes. """
        int1= Tag.objects.create(user = self.user, name='x1')
        int2= Tag.objects.create(user = self.user, name='x2')

        recipe = create_recipe(user = self.user)
        recipe.tags.add(int1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})


        s1 = TagSerializer(int1)
        s2 = TagSerializer(int2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)


    def test_filterd_by_tag_unique(self):
        """ Test filtered tag return unique list """

        int1= Tag.objects.create(user = self.user, name='eggs')
        Tag.objects.create(user = self.user, name='x2')

        recipe1 = create_recipe(user = self.user, title = 'eggs fries')
        recipe2 = create_recipe(user = self.user, title = 'eggs blowed')

        recipe1.tags.add(int1)
        recipe2.tags.add(int1)


        res = self.client.get(TAGS_URL, {'assigned_only': 1})



        self.assertEqual(len(res.data), 1)