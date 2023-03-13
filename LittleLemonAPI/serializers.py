from rest_framework import serializers 
from django.contrib.auth.models import Group
from .models import MenuItem, Category, CustomUser, CartItem, Cart, Order, OrderItem
from rest_framework.authtoken.models import Token

from decimal import Decimal

class GroupNameSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)

        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category 
        fields = ["id", "title", "slug"]


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ["key", "created"]


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    token = TokenSerializer(read_only=True, source="auth_token")
    groups = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = CustomUser 
        fields = ["id", "username", "email", "first_name", "last_name", "token", "password", "groups"]
    
    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = MenuItem 
        fields = ["id", "title", "price", "featured", "category", "category_id"]
    
    def calculate_tax(self, product:MenuItem):
        return product.price * Decimal(1.1)


class CartItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(many=False, read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem 
        fields = ["id", "menuitem", "unit_price", "quantity", "price", "menuitem_id"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart 
        fields = ["id", "total", "items"]
    

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem 
        fields = ["id", "quantity", "unit_price", "price", "menuitem", "menuitem_id"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Order 
        fields = ["id", "status", "total", "items", "user_id"]
    