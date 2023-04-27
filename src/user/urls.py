from django.urls import path

from user.views import CreateUserView, RetrieveUserView

app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('<int:pk>/', RetrieveUserView.as_view(), name='retrieve')
]
