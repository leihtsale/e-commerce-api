from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.filters import ProductFilter
from core.models import Product
from products.serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ProductFilter
    search_fields = ['name']
    ordering_fields = ['price', 'total_sold', 'rating', 'created_at']

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload_image',
            parser_classes=[MultiPartParser])
    def upload_image(self, request, pk=None):
        product = self.get_object()
        image = request.FILES.get('image')

        if image:
            product.image = image
            product.save()
            return Response({'detail': 'Image uploaded.'},
                            status=status.HTTP_200_OK)

        return Response({'detail': 'Image not found.'},
                        status=status.HTTP_400_BAD_REQUEST)


class PublicProductView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filterset_class = ProductFilter
    search_fields = ['name']
    ordering_fields = ['price', 'total_sold', 'rating', 'created_at']


class PublicProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
