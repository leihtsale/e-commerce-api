from django.contrib import admin
from django.contrib.auth import get_user_model
from core.models import (Product, Category,
                         Cart, OrderItem, Order)


admin.site.register(get_user_model())
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(OrderItem)
admin.site.register(Order)
