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


class AutoRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Extract the access and refresh tokens from the request cookies
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        # Check if the tokens are available and need refreshing
        if access_token and refresh_token:
            refresh_token_obj = RefreshToken(refresh_token)
            access_token_obj = AccessToken(access_token)
            access_token_lifetime = api_settings.ACCESS_TOKEN_LIFETIME

            # Calculate the token's remaining lifetime
            token_remaining_lifetime = (
                access_token_obj.payload.get('exp') -
                int(datetime.now().timestamp())
            )
            # Refresh the token if its remaining lifetime is less than a specified threshold
            refresh_threshold = 60  # Set the threshold in seconds
            if token_remaining_lifetime <= refresh_threshold:
                new_access_token = refresh_token_obj.access_token
                response.set_cookie(
                    'access_token', str(new_access_token),
                    httponly=True,
                    max_age=access_token_lifetime.seconds,
                )

        return response
