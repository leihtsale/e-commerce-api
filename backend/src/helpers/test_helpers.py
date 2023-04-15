from django.contrib.auth import get_user_model
from core.models import Product


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
