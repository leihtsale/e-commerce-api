from django.urls import path
from rest_framework.routers import SimpleRouter

from products.views import ProductViewSet, PublicProductView

app_name = 'products'

router = SimpleRouter()
router.register('user/product', ProductViewSet, basename='products')

urlpatterns = [
    path('public/', PublicProductView.as_view(), name='public-list'),
    path('public/<int:pk>', PublicProductView.as_view(),
         name='public-retrieve')
]

urlpatterns += router.urls
