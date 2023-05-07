from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Order
from helpers.test_helpers import (create_carts, create_order,
                                  create_order_item, create_user)
from orders.serializers import OrderSerializer

ORDERS_URL = reverse('api:orders-list')


def detail_url(id):
    """
    Helper function to return detail url
    """
    return reverse('api:orders-detail', args=[id])


class PublicOrdersApiTests(TestCase):
    """
    Tests for unauthenticated order api calls
    """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()

    def test_list_order(self):
        """
        Fetching list of orders
        should return 401 - Unauthorized
        """
        res = self.client.get(ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fetching_single_order(self):
        """
        Fetching a single order
        should return 401 - Unauthorized
        """
        order = create_order(self.user)
        url = detail_url(order.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deleting_order(self):
        """
        Unauthenticated request to delete an order
        should return 401 - Unauthorized
        """
        order = create_order(self.user)
        url = detail_url(order.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateOrdersApiTests(TestCase):
    """
    Tests for authenticated orders api requests
    """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.sample_shipping_info = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'address': 'Some address',
            'city': 'some city',
            'zipcode': 3021,
        }

    def test_list_orders(self):
        """
        Fetching list of orders
        should return 200 - OK and
        return the list of orders for the current user
        """
        for _ in range(5):
            create_order(self.user)

        orders = Order.objects.filter(user=self.user)
        serialized_orders = OrderSerializer(orders, many=True)
        res = self.client.get(ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(sorted(res.data['results'], key=lambda x: x['id']),
                         sorted(serialized_orders.data, key=lambda x: x['id']))

    def test_fetch_single_order(self):
        """
        Fetching a single order
        should return 200 - OK and return a single order
        """
        order = create_order(self.user)
        serialized_order = OrderSerializer(order)
        url = detail_url(order.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_order.data)

    def test_create_order(self):
        """
        Creating an order
        should return 201 - Created and return the order
        """
        initial_order_count = Order.objects.filter(user=self.user).count()
        carts = create_carts(self.user, quantity_per_cart_item=1)
        payload = {
            'cart_ids': [cart.id for cart in carts],
            'shipping_info': self.sample_shipping_info,
        }
        res = self.client.post(ORDERS_URL, payload, format='json')
        current_count = Order.objects.filter(user=self.user).count()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(current_count, initial_order_count + 1)

    def test_create_order_product_inventory(self):
        """
        Successful order
        should return 201 - Created and increate the product inventory
        """
        initial_order_count = Order.objects.filter(user=self.user).count()
        carts = create_carts(self.user, quantity_per_cart_item=1)
        payload = {
            'cart_ids': [cart.id for cart in carts],
            'shipping_info': self.sample_shipping_info,
        }
        res = self.client.post(ORDERS_URL, payload, format='json')
        current_count = Order.objects.filter(user=self.user).count()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(current_count, initial_order_count + 1)

        for cart in carts:
            product = cart.product
            product.refresh_from_db()
            # total_sold should increase by one, since the
            # quantity per cart is set only to one
            # carts = create_carts(self.user, quantity_per_cart_item=1)
            self.assertEqual(product.total_sold, 1)

    def test_create_order_with_insufficient_product_inventory(self):
        """
        Attempt to create an order while product inventory is less than
        the cart quantity
        should return 400 - Bad Request and not process the order
        """
        initial_order_count = Order.objects.filter(user=self.user).count()

        # The default product inventory within these carts is 1
        carts = create_carts(self.user, quantity_per_cart_item=5)

        payload = {
            'cart_ids': [cart.id for cart in carts],
            'shipping_info': self.sample_shipping_info,
        }
        res = self.client.post(ORDERS_URL, payload, format='json')
        current_count = Order.objects.filter(user=self.user).count()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(current_count, initial_order_count)

    def test_update_order(self):
        """
        Updating an order is not allowed
        should return 405 - Method not allowed
        """
        cart = create_carts(self.user, quantity_per_cart_item=1)[0]
        order = create_order(self.user)
        order_item = create_order_item(order, cart)
        inventory_after_order_create = order_item.product.inventory
        total_sold_after_order_create = order_item.product.total_sold
        url = detail_url(order.id)
        payload = {
            'is_cancelled': True,
        }
        res = self.client.patch(url, payload)
        order_item.refresh_from_db()
        product = order_item.product

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(inventory_after_order_create + 1, product.inventory)
        self.assertEqual(total_sold_after_order_create - 1, product.total_sold)

    def test_delete_order(self):
        """
        Deleting an order
        should return 204
        """
        order = create_order(self.user)
        url = detail_url(order.id)
        res = self.client.delete(url)
        orders = Order.objects.filter(user=self.user)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(orders.exists())
