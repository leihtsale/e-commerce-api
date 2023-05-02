from rest_framework import serializers

from core.models import Category, Product


class CategoryListField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        try:
            category = Category.objects.get(name=data.lower())
            return category
        except Category.DoesNotExist:
            raise serializers.ValidationError(f"Category not found: {data}")


class ProductSerializer(serializers.ModelSerializer):
    categories = CategoryListField(
        queryset=Category.objects.all(), many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'inventory', 'image',
            'description', 'rating', 'total_sold',
            'categories', 'created_at', 'updated_at']
        extra_kwargs = {
            'id': {'read_only': True},
            'image': {'read_only': True},
            'categories': {'read_only': True},
            'description': {'required': False, 'allow_blank': True},
            'rating': {'read_only': True},
            'total_sold': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

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
