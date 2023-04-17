from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from core.models import Product
from products import serializers
from helpers.test_helpers import (
    create_user,
    create_product
)

PRODUCTS_URL = reverse('api:products-list')


def detail_url(id):
    """
    Helper function to return the url for a product with the params id
    """
    return reverse('api:products-detail', args=[id])


class PublicProductApiTests(TestCase):
    """
    Tests for unauthenticated Product API calls
    """
    def setUp(self):
        self.client = APIClient()

    def test_fetching_products(self):
        """
        Unauthenticated fetching of products
        should return 401 - Unauthorized
        """
        res = self.client.get(PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductApiTests(TestCase):
    """
    Tests for authenticated Product API calls
    """
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@email.com',
            password='userpassword',
            username='userusername',
            first_name='user firstname',
            last_name='user lastname'
        )
        self.client.force_authenticate(self.user)

    def test_fetching_products(self):
        """
        Authenticated fetching of products
        should return 200 - OK
        and the list of products for the current user
        """
        create_product(user=self.user)
        res = self.client.get(PRODUCTS_URL)
        products = Product.objects.filter(user=self.user)
        serialized_data = serializers.ProductSerializer(products, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_data.data)

    def test_creating_product(self):
        """
        Authenticated creating of product
        should return 201 - Created
        and return the product data
        """
        payload = {
            'name': 'Generic product',
            'price': 1,
            'inventory': 1,
            'description': 'My description',
        }
        res = self.client.post(PRODUCTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['name'], payload['name'])

    def test_creating_product_with_read_only_field(self):
        """
        Creating a product with ready only fields
        should return 400 - Bad Request
        """
        payload = {
            'name': 'Test product',
            'price': 1,
            'inventory': 1,
            'description': 'My description',
            'rating': 1
        }
        res = self.client.post(PRODUCTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_full_update_product(self):
        """
        Full update on a product
        should return 200 - OK
        """
        product = create_product(self.user)
        payload = {
            'name': 'New name',
            'price': 10,
            'inventory': 50,
            'description': 'New description'
        }
        url = detail_url(product.id)
        res = self.client.put(url, payload)
        product.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)

    def test_patch_update_product(self):
        """
        Updating a specific field on a product
        should return 200 - OK
        """
        product = create_product(self.user)
        payload = {
            'name': 'New product name',
        }
        url = detail_url(product.id)
        res = self.client.patch(url, payload)
        product.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], payload['name'])
        self.assertEqual(product.name, payload['name'])

    def test_updating_other_user_product(self):
        """
        Attempt to update other user's product
        should return 404 - Not Found
        since the other user's product doesn't exists
        for the current user
        """
        another_user = create_user()
        another_product = create_product(another_user)
        payload = {
            'user': self.user,
        }
        url = detail_url(another_product.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_deleting_product(self):
        """
        Deleting a product
        should return 204 - No Content
        """
        product = create_product(self.user)
        url = detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(user=self.user).exists())

    def test_deleting_other_user_product(self):
        """
        Deleting other user's product
        should return 404 - Not Found
        """
        another_user = create_user()
        product = create_product(another_user)
        url = detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Product.objects.filter(user=another_user).exists())
