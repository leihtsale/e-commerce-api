from django_filters import rest_framework as filters

from core.models import Product


class ProductFilter(filters.FilterSet):
    """
    Filter for Products
    """
    categories = filters.CharFilter(method='filter_by_categories')
    min_rating = filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = filters.NumberFilter(field_name='rating', lookup_expr='lte')
    price = filters.RangeFilter(field_name='price')

    class Meta:
        model = Product
        fields = ['categories', 'min_rating',
                  'max_rating', 'price']

    def filter_by_categories(self, queryset, name, value):
        category_names = value.split(',')
        return queryset.filter(categories__name__in=category_names).distinct()
