from rest_framework.routers import SimpleRouter
from . import views


router = SimpleRouter()
router.register('products', views.ProductViewSet, basename='products')
