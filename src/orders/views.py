from rest_framework import permissions, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Order, OrderItem
from orders.serializers import OrderItemSerializer, OrderSerializer


class OrdersViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)
