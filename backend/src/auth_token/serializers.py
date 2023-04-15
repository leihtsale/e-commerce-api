from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _


class TokenSerializer(serializers.Serializer):
    """
    Serializer for token generation
    """
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs):
        """
        Authenticating user with the provided credential
        """
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context['request'],
            email=email,
            password=password
        )

        if not user:
            msg = _('Invalid email or password.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user

        return attrs
