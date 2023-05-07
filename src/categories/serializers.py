from core.models import Category
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for categories
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at']
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }
