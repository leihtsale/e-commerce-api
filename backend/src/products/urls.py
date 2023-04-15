from rest_framework.routers import SimpleRouter
from . import views

app_name = 'products'

router = SimpleRouter()
router.register('products', views.ProductViewSet, basename='products')
