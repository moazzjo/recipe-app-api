"""
Test for the user API. 
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient # type: ignore
from rest_framework import status # type: ignore


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """ Create and returna new user. """
    return get_user_model().objects.create_user(**params)

class PublicUserApiTest(TestCase):
    """ Test the public features of the user API. """

    def setUp(self):
        self.client = APIClient()


    def test_create_user_success(self):
        """ Test creating a user is successful. """
        payload = {
            'email' :'test@example.com',
            'password' :'testpass1234',
            'name': 'Test Name',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email = payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data )

    def test_user_with_email_exists_error(self):
        """ Test error return if user with email exists. """
        payload = {
            'email' :'test@example.com',
            'password' :'testpass1234',
            'name': 'Test Name',
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST) 

    def test_if_password_too_short_error(self):
        """ Test if the password less than 5 return error. """
        payload = {
            'email' :'test@example.com',
            'password' :'we',
            'name': 'Test Name',
        }
        res= self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email = payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ Test generats token for valid credentiales. """
        user_details = {
            'email' :'test@example.com',
            'password' :'test-pass-1234',
            'name': 'Test Name',
        }

        create_user(**user_details)

        payload = {
            'email' : user_details['email'],
            'password' : user_details['password']
        }



        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        create_user(email='test@example.com', password='goodpass')

        payload = {'email': 'test@example.com', 'password': 'badpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_token_blank_password(self):
        """ Test posting a blanlk password return errors. """
        paylaod = {"email":'test@example.com', "password":''}
        res = self.client.post(TOKEN_URL, paylaod)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """ Test authentication is required for user. """

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """ Test API REQUESTS that require authentication. """

    def setUp(self):
        self.user = create_user(
            email = 'test@example.com',
            password = 'password1234',
            name= 'Test Name',
        )

        self.client= APIClient()
        self.client.force_authenticate(user = self.user)

    def test_retreive_profile_success(self):
        """ Test retreiving profile for logged in user. """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name' : self.user.name,
            'email': self.user.email,
        })
    

    def test_post_me_not_allowed(self):
        """ Test POST is not allowed for the me endpoint. """
        res = self.client.post(ME_URL, {})
        

        self.assertEqual(res.status_code , status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ Test updating the user profile for the authenticated user. """
        paylaod = { 'name': 'Updated Name' , 'password': 'updatedPassword1234'}

        res = self.client.patch(ME_URL, paylaod)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, paylaod['name'])
        self.assertTrue(self.user.check_password(paylaod['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)



               







