from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model


class EmailBackend(BaseBackend):
    """
    Custom backend for authenticating with Email
    """
    def authenticate(self, request, email=None, password=None):

        try:
            user = get_user_model().objects.get(email=email)

        except get_user_model().DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None

    def get_user(self, id):

        try:
            return get_user_model().objects.get(pk=id)

        except get_user_model().DoesNotExist:
            return None
