from rest_framework.test import APIClient
from rest_framework import status

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


CREATE_TOKEN_URL = reverse('token:create')


class PublicTokenApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='example@email.com',
            password='testpass',
            username='myusername',
            first_name='First Name',
            last_name='Last Name'
        )

    def test_create_token_with_valid_user_credentials(self):
        """
        Submitting a valid credential
        should return a token
        """
        payload = {
            'email': 'example@email.com',
            'password': 'testpass',
        }
        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_with_invalid_user_credentials(self):
        """
        Submitting an invalid credential
        should return 401 - Bad Request
        """
        payload = {
            'email': 'nonexistent@email.com',
            'password': 'testpass',
        }
        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
