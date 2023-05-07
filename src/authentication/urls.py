from django.urls import include, path

from authentication.views import (CheckAuthenticationView,
                                  CookieTokenObtainView,
                                  CookieTokenRefreshView, LogoutView)

app_name = 'token'

urlpatterns = [
    path('', CookieTokenObtainView.as_view(), name='create'),
    path('verify_login/', CheckAuthenticationView.as_view(),
         name='verify_login'),
    path('refresh/', CookieTokenRefreshView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
