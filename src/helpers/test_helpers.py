from django.contrib.auth import get_user_model

from core.models import Cart, Category, Order, OrderItem, Product


def create_user(
        email='test@email.com', password='testpass', username='testusername',
        first_name='test firstname', last_name='test lastname', **kwargs):
    """
    Helper function for creating a user
    """
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        username=username,
        first_name=first_name,
        last_name=last_name,
        **kwargs,
    )


def create_product(
        user, name="Generic product",
        price=50, inventory=1, total_sold=0, **kwargs):
    """
    Helper function for creating a product
    """
    return Product.objects.create(
        user=user, name=name, price=price,
        inventory=inventory, total_sold=total_sold, **kwargs)


def create_carts(
        cart_user, product_user=None, count=2, quantity_per_cart_item=1):
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


def create_category(name='test category'):
    return Category.objects.create(name=name)


def create_order_item(order, cart):
    product = cart.product
    product.inventory -= cart.quantity
    product.total_sold += cart.quantity
    product.save()

    return OrderItem.objects.create(
        order=order,
        product=product,
        unit_price=cart.unit_price,
        quantity=cart.quantity,
    )


def create_order(user, shipping_info={}):

    if not shipping_info:
        shipping_info = {
            'shipping_info': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'address': 'Some address',
                'city': 'some city',
                'zipcode': 3021,
            },
        }

    return Order.objects.create(
        user=user,
        shipping_info=shipping_info,
    )
