from rest_framework import generics
from . import serializers


class CreateUserView(generics.CreateAPIView):
    serializer_class = serializers.UserSerializer
