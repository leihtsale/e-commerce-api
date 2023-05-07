from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView


class CookieTokenObtainView(TokenObtainPairView):
    """
    Sets the refresh and access token as http only cookies
    """

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
    """
    View to check if the user is authenticated
    authenticated: return the user info
    unauthenticated: raise 401 - Unauthorized
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if (request.user):
            context = {
                'username': request.user.username,
            }

            return Response(context, status=status.HTTP_200_OK)

        return Response({'Unauthorized: Please login.'},
                        status=status.HTTP_401_UNAUTHORIZED)


class CookieTokenRefreshView(APIView):
    """
    View for refreshing access token, given that the refresh_token exists
    """

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'detail': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            response = Response({'detail': 'Access token is refreshed.'})
            response.set_cookie(
                'access_token', access_token,
                httponly=True,
                max_age=api_settings.ACCESS_TOKEN_LIFETIME.total_seconds(),
            )
            return response
        except TokenError as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    Remove the cookies for tokens
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "Logout successful"},
                            status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
