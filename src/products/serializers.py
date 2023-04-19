from categories.serializers import CategorySerializer
from core.models import Category, Product
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):

    categories = CategorySerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'name', 'price', 'inventory', 'description',
            'rating', 'total_sold', 'categories',
            'created_at', 'updated_at']
        extra_kwargs = {
            'rating': {'read_only': True},
            'total_sold': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def _get_categories(self, categories):
        """
        Helper function to get the categories by name
        :return: Array of Category
        """
        category_list = []
        for category in categories:
            try:
                existing_category = Category.objects.get(
                    name=category['name'].lower()
                )
                category_list.append(existing_category)
            except Category.DoesNotExist:
                raise serializers.ValidationError(
                    f"Category not found: {category['name']}"
                )
        return category_list

    def create(self, validated_data):
        """
        Modify the create, to remove the categories in validate_data
        and get all the categories by name with _get_categories
        helper function. And if the categories exists,
        assign it to the product
        """
        categories = validated_data.pop('categories', [])
        existing_categories = self._get_categories(categories)
        product = Product.objects.create(**validated_data)

        for category in existing_categories:
            product.categories.add(category)

        return product

    def update(self, instance, validated_data):
        """
        Modify the update, to remove the categories in validate_data
        and get all the categories by name with _get_categories
        helper function. And if the categories exists,
        assign it to the product
        """
        categories = validated_data.pop('categories', [])

        if categories is not None:
            instance.categories.clear()
            existing_categories = self._get_categories(categories)

            for category in existing_categories:
                instance.categories.add(category)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance

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
