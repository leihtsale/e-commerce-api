from core.models import Cart
from rest_framework import serializers


class CartSerializer(serializers.ModelSerializer):

    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'user', 'product', 'unit_price', 'total',
            'quantity', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'user': {'read_only': True},
            'unit_price': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def get_total(self, instance):
        """
        Calculate the total price of the cart item based
        on the unit price and quantity.
        """
        return instance.get_total()


class CartDetailSerializer(CartSerializer):

    class Meta(CartSerializer.Meta):
        extra_kwargs = dict(CartSerializer.Meta.extra_kwargs)
        extra_kwargs.update({'product': {'read_only': True}})

    def validate(self, attrs):
        """
        Validate the incoming data for creating or updating a cart item.

        This method ensures that only the 'quantity' field can be updated
        during a partial update (PATCH) operation. If any other field is
        attempted to be updated, a ValidationError is raised.

        :raises: ValidationError if a disallowed field is found during an
                    update operation.
        """
        allowed_fields = ('quantity',)
        is_update = self.instance is not None

        if (is_update):
            for field in attrs.keys():
                if field not in allowed_fields:
                    raise serializers.ValidationError(
                        f'Only the quantity field can be updated. {field} \
                            is not allowed.'
                    )

        return attrs

    def to_internal_value(self, data):
        """
        This method raises an error if there is an attempt to update
        a read_only field, instead of just ignoring it.

        :raises: ValidationError
        """
        for field_name, field in self.fields.items():
            if field.read_only and field_name in data:
                raise serializers.ValidationError({
                    field_name: "This field is read-only."
                })
        return super().to_internal_value(data)
