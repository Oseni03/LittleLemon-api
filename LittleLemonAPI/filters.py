from django_filters import rest_framework as filters
from .models import MenuItem, Order


class MenuItemFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="category__slug", lookup_expr='iexact')
    search = filters.CharFilter(field_name="title", lookup_expr='icontains')
    price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    ordering = filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('price', 'price'),
            ('title', 'title'),
            ('category', 'category'),
        ),
    )

    class Meta:
        model = MenuItem
        fields = ['category', 'title', "price"]


class OrderFilter(filters.FilterSet):
    status = filters.CharFilter(field_name="status", lookup_expr='exact')
    
    class Meta:
        model = Order
        fields = ['status']