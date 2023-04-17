from carts.serializers import CartDetailSerializer, CartSerializer
from core.models import Cart
from rest_framework import permissions, viewsets
from rest_framework.authentication import TokenAuthentication


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options', 'patch', 'delete']

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if (self.action == 'create' or self.action == 'list'):
            return CartSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
