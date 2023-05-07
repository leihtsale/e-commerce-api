from django.urls import path

from payments.views import (CartCheckoutSession, DirectCheckoutSession,
                            StripeWebHook)

app_name = 'payments'

urlpatterns = [
    path('stripe_webhook', StripeWebHook.as_view(), name='stripe_webhook'),
    path('direct_checkout/', DirectCheckoutSession.as_view(), name='direct_checkout'),
    path('cart_checkout/', CartCheckoutSession.as_view(),
         name='cart_checkout'),
]
