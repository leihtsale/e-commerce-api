from django.urls import path, include
from products.urls import router as product_router

urlpatterns = [
    path('user/', include('user.urls')),
    path('token/', include('auth_token.urls')),
    path('', include((product_router.urls, 'products'))),
]
