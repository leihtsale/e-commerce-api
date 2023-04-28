from django.urls import path

from authentication.views import (
    CookieTokenObtainView,
    CheckAuthenticationView,
    LogoutView)

app_name = 'token'

urlpatterns = [
    path('', CookieTokenObtainView.as_view(), name='create'),
    path('verify_login/', CheckAuthenticationView.as_view(),
         name='verify_login'),
    path('logout/', LogoutView.as_view(), name='logout')
]
