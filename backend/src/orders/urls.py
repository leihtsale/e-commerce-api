from orders.views import OrdersViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('orders', OrdersViewSet, basename='orders')
