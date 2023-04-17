from categories.views import CategoryViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('categories', CategoryViewSet, basename='categories')
