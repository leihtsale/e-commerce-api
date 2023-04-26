from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.settings import api_settings

class CookieTokenObtainView(TokenObtainPairView):
    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code == 200:
            access_token = response.data.pop('access')
            refresh_token = response.data.pop('refresh')
            response.set_cookie(
                'refresh_token', refresh_token,
                httponly=True,
                max_age=api_settings.REFRESH_TOKEN_LIFETIME.total_seconds(),
            )
            response.set_cookie(
                'access_token', access_token,
                httponly=True,
                max_age=api_settings.ACCESS_TOKEN_LIFETIME.total_seconds(),
            )
        return super().finalize_response(request, response, *args, **kwargs)
