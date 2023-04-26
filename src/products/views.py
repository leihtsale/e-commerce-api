from rest_framework import permissions, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Product
from products.serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
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
