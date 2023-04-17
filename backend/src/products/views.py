from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets, permissions
from core.models import Product
from . import serializers


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProductSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if (self.action == 'list' or self.action == 'retrieve'):
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        if (self.action == 'list' or self.action == 'retrieve'):
            return Product.objects.all()
        return Product.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
