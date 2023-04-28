from rest_framework import generics, permissions, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Product
from products.serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicProductView(
        generics.ListAPIView,
        generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
