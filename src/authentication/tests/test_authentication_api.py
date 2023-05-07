from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_TOKEN_URL = reverse('token:create')


class AuthenticationTokenApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='example@email.com',
            password='testpass',
            username='myusername',
            first_name='First Name',
            last_name='Last Name'
        )

    def test_obtain_token(self):
        """
        Tokens are set as http only cookies
        should return 200 - OK, and set the tokens in cookies
        """
        payload = {
            'email': 'example@email.com',
            'password': 'testpass',
        }
        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', res.cookies)
        self.assertIn('refresh_token', res.cookies)

    def test_obtain_token_with_invalid_credentials(self):
        """
        Attempt to obtain token with invalid credentials
        should return 401 - Unauthorized
        """
        payload = {
            'email': 'example@email.com',
            'password': 'badpass',
        }
        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
