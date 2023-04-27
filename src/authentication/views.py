from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication


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


class CheckAuthenticationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            'is_authenticated': True,
            'id': request.user.id,
            'email': request.user.email,
            'username': request.user.username,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,

        }
        return Response(context, status=status.HTTP_200_OK)
