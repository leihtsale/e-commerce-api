from rest_framework import serializers
from core.models import Product


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            'name', 'price', 'inventory',
            'description', 'rating', 'total_sold',
            'created_at', 'updated_at']
        extra_kwargs = {
            'rating': {'read_only': True},
            'total_sold': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def to_internal_value(self, data):
        for field_name, field in self.fields.items():
            if field.read_only and field_name in data:
                raise serializers.ValidationError({
                    field_name: "This field is read-only."
                })
        return super().to_internal_value(data)
