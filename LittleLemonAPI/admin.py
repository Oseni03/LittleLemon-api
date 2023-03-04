from django.contrib import admin
from .models import Cart, CartItem, CustomUser

# Register your models here.
@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display =("username", "email", "first_name", "last_name", "is_staff")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display =("user", "total")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display =("cart", "quantity", "menuitem", "unit_price", "price")