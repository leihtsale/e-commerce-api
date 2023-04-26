from django.urls import path

from authentication.views import CookieTokenObtainView

app_name = 'token'

urlpatterns = [
    path('', CookieTokenObtainView.as_view(), name='create'),
]
