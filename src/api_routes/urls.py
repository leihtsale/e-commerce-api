from carts.urls import router as carts_router
from categories.urls import router as categories_router
from django.urls import include, path
from orders.urls import router as orders_router
from products.urls import router as product_router
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.registry.extend(product_router.registry)
router.registry.extend(carts_router.registry)
router.registry.extend(categories_router.registry)
router.registry.extend(orders_router.registry)

urlpatterns = [
    path('user/', include('user.urls')),
    path('token/', include('authentication.urls')),
    path('', include((router.urls, 'api')))
]
