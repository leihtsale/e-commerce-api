from categories.serializers import CategorySerializer
from core.models import Category
from rest_framework import permissions, viewsets
from rest_framework.authentication import TokenAuthentication


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_permissions(self):
        if (self.action == 'list' or self.action == 'retrieve'):
            return [permissions.AllowAny()]
        return super().get_permissions()
