from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.settings import api_settings


class AddBearerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.COOKIES.get('access_token')
        if access_token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        response = self.get_response(request)
        return response
