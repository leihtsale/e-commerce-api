from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product
from helpers.test_helpers import create_category, create_product, create_user
from products.serializers import ProductSerializer

PRODUCTS_URL = reverse('products:products-list')
PUBLIC_PRODUCTS_URL = reverse('products:public-list')


def public_detail_url(id):
    """
    Helper function to return the url for a product with the params id
    """
    return reverse('products:public-retrieve', args=[id])


def detail_url(id):
    return reverse('products:products-detail', args=[id])


class PublicProductApiTests(TestCase):
    """
    Tests for unauthenticated Product API calls
    """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()

    def test_list_products(self):
        """
        Fetching list of products
        should return 200 - OK and return the list of products
        """
        for _ in range(5):
            create_product(self.user)
        products = Product.objects.all()
        serialized_products = ProductSerializer(products, many=True)
        res = self.client.get(PUBLIC_PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_products.data)

    def test_fetching_single_product(self):
        """
        Fetching a single category
        should return 200 - OK and return a single product
        """
        product = create_product(self.user)
        serialized_product = ProductSerializer(product)
        url = public_detail_url(product.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(dict(res.data[0]), serialized_product.data)

    def test_updating_product(self):
        """
        Unauthenticated request to update a product
        should return 401 - Unauthorized
        """
        product = create_product(self.user)
        url = detail_url(product.id)
        res = self.client.patch(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deleting_product(self):
        """
        Unauthenticated request to delete a product
        should return 401 - Unauthorized
        """
        product = create_product(self.user)
        url = detail_url(product.id)
        res = self.client.delete(url)

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

    def test_list_products(self):
        """
        Fetching list of products
        should return 200 - OK and
        return the list of products for the current user
        """
        for _ in range(5):
            create_product(user=self.user)
        products = Product.objects.all()
        serialized_data = ProductSerializer(products, many=True)
        res = self.client.get(PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_data.data)

    def test_fetch_single_product(self):
        """
        Fetching a single product
        should return 200 - OK and return a single product
        """
        product = create_product(self.user)
        serialized_product = ProductSerializer(product)
        url = detail_url(product.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_product.data)

    def test_create_product(self):
        """
        Creating a product
        should return 201 - Created and return the product
        """
        initial_product_count = Product.objects.filter(user=self.user).count()
        payload = {
            'name': 'Generic product',
            'price': 1,
            'inventory': 1,
            'description': 'My description',
        }
        res = self.client.post(PRODUCTS_URL, payload)
        current_count = Product.objects.filter(user=self.user).count()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(current_count, initial_product_count + 1)
        self.assertEqual(res.data['name'], payload['name'])

    def test_create_product_with_existing_category(self):
        """
        Creating a product and assigning an existing category
        should return 201 - Created, creating the product
        with the category assigned to it
        """
        create_category(name='Tech')
        initial_products_count = Product.objects.filter(user=self.user).count()
        payload = {
            'name': 'Generic product',
            'price': 1,
            'inventory': 1,
            'description': 'My description',
            'categories': [{'name': 'Tech'}],
        }
        res = self.client.post(PRODUCTS_URL, payload, format='json')
        product = Product.objects.filter(user=self.user).first()
        serialized_product = ProductSerializer(product)
        current_count = Product.objects.filter(user=self.user).count()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(current_count, initial_products_count + 1)
        self.assertEqual(res.data, serialized_product.data)

        for category in payload['categories']:
            c = product.categories.filter(name=category['name'].lower())
            self.assertTrue(c.exists())

    def test_create_product_with_nonexistent_category(self):
        """
        Attempt to add a nonexistent category on a product on create,
        should return 400 - Bad Request
        """
        payload = {
            'name': 'Generic product',
            'price': 1,
            'inventory': 1,
            'description': 'My description',
            'categories': [{'name': 'Tech'}],
        }
        res = self.client.post(PRODUCTS_URL, payload, format='json')
        products = Product.objects.filter(user=self.user)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(products.exists())

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

    def test_updating_product_with_existing_category(self):
        """
        Adding an existing category to a product
        should return 200 - OK
        """
        create_category(name='Sample Category')
        product = create_product(self.user)
        payload = {
            'categories': [{'name': 'sample Category'}]
        }
        url = detail_url(product.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        for category in payload['categories']:
            c = product.categories.filter(name=category['name'].lower())
            self.assertTrue(c.exists())

    def test_updating_product_with_nonexistent_category(self):
        """
        Attempt to update a product by assigning a nonexistent category
        should return 400 - Bad Request
        """
        product = create_product(self.user)
        payload = {
            'categories': [{'name': 'Nonexistent category'}]
        }
        url = detail_url(product.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(product.categories.exists())

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
