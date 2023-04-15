from rest_framework.authtoken.views import ObtainAuthToken
from . import serializers


class CreateTokenView(ObtainAuthToken):
    """
    Make the ObtainAuthToken to use the custom serializer
    """
    serializer_class = serializers.TokenSerializer
