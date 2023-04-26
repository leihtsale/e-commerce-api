from rest_framework import permissions, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from categories.serializers import CategorySerializer
from core.models import Category


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_permissions(self):
        if (self.action == 'list' or self.action == 'retrieve'):
            return [permissions.AllowAny()]
        return super().get_permissions()
