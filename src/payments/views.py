import stripe
from django.conf import settings
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import (
    JWTAuthentication)

from core.models import Order, OrderItem, Product
from orders.serializers import OrderSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeWebHook(views.APIView):
    """
    Stripe webhook for success checkout
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(StripeWebHook, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return Response({'error': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.SignatureVerificationError as e:
            return Response({'error': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            status_code, error_msg = handle_successful_payment(session)

            if status_code != status.HTTP_200_OK:
                return Response({'error': error_msg}, status=status_code)

        return Response({}, status=status.HTTP_200_OK)


class DirectCheckoutSession(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        shipping_info = request.data.get('shipping_info', {})
        user = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exists.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if quantity <= product.inventory and quantity > 0:

            with transaction.atomic():
                try:
                    order = Order.objects.create(
                        user=user,
                        shipping_info=shipping_info,
                        status=Order.PENDING)

                    order_item = OrderItem.objects.create(
                        order=order, product=product,
                        unit_price=product.price, quantity=quantity)

                    product.inventory -= quantity
                    product.total_sold += quantity
                    product.save()

                except IntegrityError:
                    return Response(
                        {'error': 'Unable to process your order.'},
                        status=status.HTTP_400_BAD_REQUEST)

        item = [{
                'price_data': {
                    'currency': 'PHP',
                    'product_data': {
                        'name': order_item.product.name,
                    },
                    'unit_amount': int(order_item.unit_price * 100),
                },
                'quantity': order_item.quantity,
                }]

        status_code, data = create_stripe_checkout(item, order.id)

        if status_code != status.HTTP_200_OK:
            return Response({'error': data}, status=status_code)

        return Response({'id': data}, status=status.HTTP_200_OK)


class CartCheckoutSession(views.APIView):
    """
    View for creating a Stripe session
    success: returns a session id
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart_ids = request.data.get('cart_ids', [])
        shipping_info = request.data.get('shipping_info', {})
        user = request.user
        order_data = {
            'cart_ids': cart_ids,
            'shipping_info': shipping_info,
            'status': Order.PENDING
        }

        order_serializer = OrderSerializer(data=order_data)

        if not order_serializer.is_valid():
            return Response(order_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        pending_order = order_serializer.save(user=user)

        order_items = []
        for order_item in pending_order.order_items.all():
            order_items.append({
                'price_data': {
                    'currency': 'PHP',
                    'product_data': {
                        'name': order_item.product.name,
                    },
                    'unit_amount': int(order_item.unit_price * 100),
                },
                'quantity': order_item.quantity,
            })

        status_code, data = create_stripe_checkout(
            order_items, pending_order.id)

        if status_code != status.HTTP_200_OK:
            return Response({'error': data}, status=status_code)

        return Response({'id': data}, status=status.HTTP_200_OK)


"""
Helper functions
"""


def create_stripe_checkout(line_items, order_id):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            metadata={
                'order_id': order_id
            },
            success_url=settings.PAYMENT_SUCCESS_URL
        )
    except Exception:
        return (status.HTTP_500_INTERNAL_SERVER_ERROR,
                'Something went wrong.')

    Order.objects.filter(id=order_id).update(
        stripe_checkout_session_id=checkout_session.id)
    return status.HTTP_200_OK, checkout_session.id


def handle_successful_payment(session):
    order_id = session['metadata']['order_id']

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return (status.HTTP_404_NOT_FOUND,
                f'Order with ID {order_id} does not exist',)
    serializer = OrderSerializer(
        order, data={'status': Order.PAID}, partial=True)

    if serializer.is_valid():
        serializer.save()
        return status.HTTP_200_OK, ''
    else:
        return (status.HTTP_400_BAD_REQUEST,
                f'Failed to update Order with ID {order_id}.',)
