from django.contrib.auth import get_user_model
from core.models import Product
from core.models import Cart


def create_user(
        email='test@email.com', password='testpass', username='testusername',
        first_name='test firstname', last_name='test lastname'):
    """
    Helper function for creating a user
    """
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        username=username,
        first_name=first_name,
        last_name=last_name,
    )


def create_product(
        user, name="Generic product",
        price=1, inventory=1, total_sold=0, **kwargs):
    """
    Helper function for creating a product
    """
    return Product.objects.create(
        user=user, name=name, price=price,
        inventory=inventory, total_sold=total_sold, **kwargs)


def create_carts(cart_user, product_user, count=2, quantity_per_cart_item=5):
    """
    Helper function for creating carts
    """
    carts = []
    for _ in range(count):
        product = create_product(product_user if product_user else cart_user)
        cart = Cart.objects.create(
            user=cart_user,
            product=product,
            quantity=quantity_per_cart_item,
        )
        carts.append(cart)

    return carts
