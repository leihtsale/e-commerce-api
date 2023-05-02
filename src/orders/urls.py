from rest_framework.routers import SimpleRouter

from orders.views import OrderItemViewSet, OrdersViewSet

router = SimpleRouter()
router.register('orders', OrdersViewSet, basename='orders')
router.register('order_items', OrderItemViewSet, basename='order_items')
