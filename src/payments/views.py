import stripe
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Order
from orders.serializers import OrderSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeWebHook(views.APIView):
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

        print(event['type'])
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            handle_successful_payment(session)

        return Response({}, status=status.HTTP_200_OK)


def handle_successful_payment(session):
    order_id = session['metadata']['order_id']

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        print(f"Order {order_id} not found.")
        return

    serializer = OrderSerializer(
        order, data={'status': Order.PAID}, partial=True)

    if serializer.is_valid():
        print(f"Order {order_id} is valid, updating status to PAID.")
        serializer.save()
    else:
        print(f"Error updating order {order_id}: {serializer.errors}")


class CreateStripeCheckoutSession(views.APIView):
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

        try:
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

            checkout_session = stripe.checkout.Session.create(
                line_items=order_items,
                mode='payment',
                metadata={
                    'order_id': pending_order.id
                },
                success_url=settings.PAYMENT_SUCCESS_URL
            )
        except Exception as e:
            print(e)
            return Response({'error': 'Something went wrong.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'id': checkout_session.id}, status=status.HTTP_200_OK)
