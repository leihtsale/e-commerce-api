from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_TOKEN_URL = reverse('token:create')
SAMPLE_PROTECTED_URL = reverse('api:carts-list')


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

    def test_auto_refresh_middleware_with_expired_access_token(self):
        """
        When the access token is near the expiration time
        the AutoRefreshMiddleware,
        should automatically refresh the access token
        """
        payload = {
            'email': 'example@email.com',
            'password': 'testpass',
        }
        obtain_token_response = self.client.post(CREATE_TOKEN_URL, payload)

        # Get the access token and refresh token from the cookies
        access_token = obtain_token_response.cookies.get('access_token').value

        # Decode the access token's payload
        decoded_payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])

        # Set a very short lifetime for the access token
        short_lifetime = timedelta(seconds=3)
        decoded_payload['exp'] = int(
            datetime.now().timestamp()) + short_lifetime.seconds

        # Re-encode the modified payload
        initial_cookie_with_short_lifetime = jwt.encode(
            decoded_payload, settings.SECRET_KEY, algorithm='HS256')

        # Set the modified access token to the client's cookies
        self.client.cookies['access_token'] = initial_cookie_with_short_lifetime

        # Test to fetch from a procted url, or a view that requires authentication
        response = self.client.get(SAMPLE_PROTECTED_URL)

        # Check if the access_token cookie is set in the response
        self.assertIn('access_token', response.cookies)

        # Assert that the access token has been refreshed
        self.assertNotEqual(
            self.client.cookies.get('access_token'), access_token)

    def test_auto_refresh_middleware_with_good_access_token(self):
        """
        Valid or not expired access token
        should not refresh
        """
        payload = {
            'email': 'example@email.com',
            'password': 'testpass',
        }
        obtain_token_response = self.client.post(CREATE_TOKEN_URL, payload)
        initial_access_token = obtain_token_response.cookies.get(
            'access_token').value

        response = self.client.get(SAMPLE_PROTECTED_URL)
        current_token = self.client.cookies.get('access_token').value


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(current_token, initial_access_token)
