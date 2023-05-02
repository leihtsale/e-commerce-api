from django.urls import path

from payments.views import CreateStripeCheckoutSession, StripeWebHook

app_name = 'payments'

urlpatterns = [
    path('checkout_session/', CreateStripeCheckoutSession.as_view(),
         name='checkout_session'),
    path('stripe_webhook', StripeWebHook.as_view(), name='stripe_webhook'),
]
