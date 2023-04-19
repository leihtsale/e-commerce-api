from carts.serializers import CartSerializer
from core.models import Cart
from django.test import TestCase
from django.urls import reverse
from helpers.test_helpers import create_carts, create_product, create_user
from rest_framework import status
from rest_framework.test import APIClient

CARTS_URL = reverse('api:carts-list')


def detail_url(id):
    """
    Helper function to return the url for a product with the params id
    """
    return reverse('api:carts-detail', args=[id])


class PublicCartsApiTests(TestCase):
    """
    Tests for unauthenticated carts api requests
    """
    def setUp(self):
        self.client = APIClient()

    def test_fetching_carts(self):
        """
        Unauthenticated fetching of carts
        should return 401 - Unauthorized
        """
        res = self.client.get(CARTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCartsApiTests(TestCase):
    """
    Tests for authenticated carts api request
    """
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='currentuser@email.com',
            password='currentuser',
            username='currentusername',
            first_name='current first name',
            last_name='current last name',
        )
        # The "seller" user is just another user, just to make sure
        # even if the product is created by another user, it can be added
        # to the cart of the current user
        self.seller = create_user(
            email="seller@email.com",
            password='sellerpassword',
            username='seller',
            first_name='seller',
            last_name='seller'
        )
        self.client.force_authenticate(self.user)

    def test_fetching_carts(self):
        """
        Authenticated fetching of carts
        should return 200 - OK
        and the list of carts for the current user
        """
        create_carts(
            cart_user=self.user,
            product_user=self.seller,
            quantity_per_cart_item=2,
        )
        res = self.client.get(CARTS_URL)
        carts = Cart.objects.filter(user=self.user)
        serialized_carts = CartSerializer(carts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(carts.exists())
        self.assertEqual(res.data, serialized_carts.data)

    def test_creating_cart(self):
        """
        Adding a product to cart
        should return 201 - Created
        """
        product = create_product(self.seller)
        payload = {
            'product': product.id,
            'quantity': 2,
        }
        initial_cart_count = Cart.objects.filter(user=self.user).count()
        res = self.client.post(CARTS_URL, payload)

        current_user_cart = Cart.objects.filter(user=self.user)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(current_user_cart.count(), initial_cart_count + 1)

        serialized_product = CartSerializer(current_user_cart.first())
        self.assertEqual(res.data, serialized_product.data)

    def test_full_update_cart(self):
        """
        Full update on a cart
        should return 405 - Method Not Allowed
        """
        carts = create_carts(
            cart_user=self.user,
            product_user=self.seller,
            count=1,
            quantity_per_cart_item=5)

        payload = {
            'quantity': 2,
        }
        url = detail_url(carts[0].id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_on_read_only_fields_cart(self):
        """
        Attempt on patch update to other fields
        should return 400 - Bad Request
        Every field in detail view is ready only, besides quantity field
        """
        carts = create_carts(
            cart_user=self.user,
            product_user=self.seller,
            count=1,
            quantity_per_cart_item=5)
        cart = carts[0]
        payload = {
            'created_at': 'test',
        }
        url = detail_url(cart.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_update_cart(self):
        """
        Only quantity is allowed for patch update
        should return 200 - OK
        """
        carts = create_carts(
            cart_user=self.user,
            product_user=self.seller,
            count=1,
            quantity_per_cart_item=5)
        cart = carts[0]
        payload = {
            'quantity': 2,
        }
        url = detail_url(cart.id)
        res = self.client.patch(url, payload)
        cart.refresh_from_db()
        serialized_cart = CartSerializer(cart)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_cart.data)

    def test_detele_cart(self):
        """
        Deleting a cart
        should return 204 - No Content
        """
        carts = create_carts(
            cart_user=self.user,
            product_user=self.seller,
            count=1,
            quantity_per_cart_item=5)
        cart = carts[0]
        url = detail_url(cart.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        check_cart = Cart.objects.filter(user=self.user)
        self.assertFalse(check_cart.exists())

    def test_delete_other_cart(self):
        """
        Attempt to delete someone's cart
        should return 404 - Not Found
        """
        carts = create_carts(
            cart_user=self.seller,
            product_user=self.seller,
            count=1,
            quantity_per_cart_item=5)
        cart = carts[0]
        url = detail_url(cart.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
