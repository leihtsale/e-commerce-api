from django.urls import path
from rest_framework.routers import SimpleRouter

from carts.views import CartCountView, CartViewSet

app_name = 'carts'

router = SimpleRouter()
router.register('carts', CartViewSet, basename='carts')

urlpatterns = [
    path('carts/count/', CartCountView.as_view(), name='count')
]

urlpatterns += router.urls
