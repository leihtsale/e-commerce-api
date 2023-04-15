from rest_framework.test import APIClient
from rest_framework import status

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


CREATE_USER_URL = reverse('user:create')


def create_user(
        email='unique@email.com',
        password='testpassword',
        username='uniqueusername',
        first_name='FirstName',
        last_name='LastName'):
    """
    Helper function to create and return a user with default values
    """
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        username=username,
        first_name=first_name,
        last_name=last_name,
    )


class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """
        Successful creation of user
        should return 201 - Created
        """
        payload = {
            'email': 'hello@example.com',
            'password': 'testpass',
            'username': 'myusername',
            'first_name': 'First',
            'last_name': 'Last'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        user = get_user_model().objects.get(email=payload['email'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_user_with_existing_email(self):
        """
        Creating a user with existing email
        should fail, return 400 - Bad Request
        """
        payload = {
            'email': 'user@example.com',
            'password': 'testpass',
            'username': 'myusername',
            'first_name': 'First',
            'last_name': 'Last'
        }
        create_user(email=payload['email'])

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_existing_username(self):
        """
        Creating a user with existing username
        should fail, return 400 - Bad Request
        """
        payload = {
            'email': 'user@example.com',
            'password': 'testpass',
            'username': 'myusername',
            'first_name': 'First',
            'last_name': 'Last'
        }
        create_user(username=payload['username'])
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_short_password(self):
        """
        Creating a user with short password
        should fail, return 400 - Bad Request
        """
        payload = {
            'email': 'user@example.com',
            'password': 'hi',
            'username': 'myusername',
            'first_name': 'First',
            'last_name': 'Last'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        user = get_user_model().objects.filter(email=payload['email'])

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user.exists())
