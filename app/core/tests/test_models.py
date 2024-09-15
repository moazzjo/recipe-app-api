"""
 Test for models
"""
from decimal import Decimal

from core import models
from django.test import TestCase
from django.contrib.auth import get_user_model


def create_user(email= 'test@example.com', password = 'test123'):
    """ create and return user. """
    return get_user_model().objects.create_user(email=email, password=password)



class ModelTest(TestCase):
    """ Test Models """

    def test_create_user_with_email_successful(self):
        """ Test for creating user with an Email is successful """
        email = 'test@example.com'
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))


    def test_new_user_email_normalized(self):
        """ Test email is normalized for new users"""

        sample_emails = [
            ['test1@EXAMPLE.COM' , 'test1@example.com'],
            ['Test2@Example.com' , 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM' , 'TEST3@example.com'],
            ['test4@example.COM' , 'test4@example.com']
        ]


        for email , expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email , expected)

    def test_new_user_without_emai_raises_error(self):
        """ Test that creating a user without email raises a valueErorr """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')


    def test_create_superuser(self):
        """ Test creating superuser """
        user = get_user_model().objects.create_superuser(
            "test@exmaple.com",
            "test123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


    def test_create_recipe(self):
        """ Test creating a recipeis successful. """
        user = get_user_model().objects.create_user(
            'test@example.com',
            'test1234',
        )


        recipe = models.Recipe.objects.create(
            user = user,
            title= 'sample recipe name',
            time_minutes = 5,
            price = Decimal('1.5'),
            description = 'sample recipe desciription'
        )

        self.assertEqual(str(recipe), recipe.title)


    def test_create_tags(self):
        """ test creating tag model. """
        user = create_user()
        tag = models.Tag.objects.create(user = user, name = 'tag1')

        self.assertEqual(str(tag), tag.name)