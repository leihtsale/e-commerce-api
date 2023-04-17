from django.urls import path, include
from rest_framework.routers import SimpleRouter
from products.urls import router as product_router
from carts.urls import router as carts_router
from categories.urls import router as categories_router

router = SimpleRouter()
router.registry.extend(product_router.registry)
router.registry.extend(carts_router.registry)
router.registry.extend(categories_router.registry)

urlpatterns = [
    path('user/', include('user.urls')),
    path('token/', include('auth_token.urls')),
    path('', include((router.urls, 'api')))
]
