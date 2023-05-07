from rest_framework import serializers

from core.models import Cart, Order, OrderItem


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model
    """

    cart_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    total = serializers.SerializerMethodField('get_total')

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'cart_ids', 'shipping_info', 'stripe_checkout_session_id',
            'status', 'is_cancelled', 'total', 'created_at', 'updated_at']
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def get_total(self, instance):
        return instance.get_total()

    def _get_carts(self, cart_ids):
        """
        Helper function to validate if the cart exists,
        if it exists, append the cart to the carts list
        """
        carts = []

        for id in cart_ids:
            try:
                cart = Cart.objects.get(pk=id)
                carts.append(cart)

            except Cart.DoesNotExist:
                raise serializers.ValidationError(
                    f'The requested cart with cart id {id}, does not exists.'
                )

        return carts

    def validate(self, attrs):
        cart_ids = attrs.pop('cart_ids', [])
        carts = self._get_carts(cart_ids)

        # Check if the requested cart quantity is less than the product inventory
        # raise ValidationError if True
        for cart in carts:
            product = cart.product
            new_inventory = product.inventory - cart.quantity

            if new_inventory < 0:
                raise serializers.ValidationError(
                    f'Insufficient inventory for product {product.name}'
                )

        attrs['carts'] = carts

        return attrs

    def create(self, validated_data):
        carts = validated_data.pop('carts', [])
        order = Order.objects.create(**validated_data)
        order_items = []

        for cart in carts:
            product = cart.product
            new_inventory = product.inventory - cart.quantity

            order_item = OrderItem(
                order=order,
                product=product,
                unit_price=product.price,
                quantity=cart.quantity,
            )

            order_items.append(order_item)
            product.inventory = new_inventory
            product.total_sold += cart.quantity
            product.save()
            cart.delete()

        OrderItem.objects.bulk_create(order_items)

        return order

    def update(self, instance, validated_data):

        # Checking if the order is canceled
        # If cancelled, revert the product quantity and inventory
        if validated_data.get('is_cancelled', False):
            order_items = OrderItem.objects.filter(order=instance)

            for order_item in order_items:
                product = order_item.product
                product.inventory += order_item.quantity
                product.total_sold -= order_item.quantity
                product.save()

        instance = super().update(instance, validated_data)
        return instance


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for items in Order
    """
    product_name = serializers.SerializerMethodField('get_product_name')
    total = serializers.SerializerMethodField('get_total')

    class Meta:
        model = OrderItem
        fields = [
            'order', 'product', 'product_name', 'unit_price',
            'quantity', 'total', 'created_at', 'updated_at']
        extra_kwargs = {
            'order': {'read_only': True},
            'product': {'read_only': True},
            'unit_price': {'read_only': True},
            'quantity': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def get_product_name(self, instance):
        return instance.get_product_name()

    def get_total(self, instance):
        return instance.get_total()
