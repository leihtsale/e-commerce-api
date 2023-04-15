from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model


class UserSerializer(ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'username', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
            }
        }

    def create(self, validated_data):
        """
        Override create to use create_user for password hashing
        """
        return get_user_model().objects.create_user(**validated_data)
