from django.urls import path
from . import views

app_name = 'token'

urlpatterns = [
    path('create/', views.CreateTokenView.as_view(), name='create'),
]
