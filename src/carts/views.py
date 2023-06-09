from rest_framework import permissions, status, views, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from carts.serializers import CartDetailSerializer, CartSerializer
from core.models import Cart


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        serialized = self.get_serializer(data=request.data)
        serialized.is_valid(raise_exception=True)
        product = serialized.validated_data.get('product')
        quantity = serialized.validated_data.get('quantity')
        user = request.user

        if Cart.objects.filter(user=user, product=product).exists():
            cart = Cart.objects.filter(user=user, product=product).first()
            cart.quantity += quantity
            cart.save()
            serialized = self.get_serializer(cart)
        else:
            self.perform_create(serialized)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if (self.action == 'create' or self.action == 'list'):
            return CartSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartCountView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Cart.objects.filter(user=request.user).count()
        return Response({'count': count}, status=200)
