from django.urls import path
from rest_framework.routers import SimpleRouter

from products.views import (ProductViewSet, PublicProductDetailView,
                            PublicProductView)

app_name = 'products'

router = SimpleRouter()
router.register('user/products', ProductViewSet, basename='products')

urlpatterns = [
    path('public/<int:pk>/', PublicProductDetailView.as_view(),
         name='public-retrieve'),
    path('public/', PublicProductView.as_view(), name='public-list'),

]

urlpatterns += router.urls
