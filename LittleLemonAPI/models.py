from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from decimal import Decimal

# Create your models here.
class CustomUser(AbstractUser):
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.username)


class Category(models.Model):
    slug = models.SlugField(db_index=True, null=True)
    title = models.CharField(max_length=255)
    
    def __str__(self):
        return str(self.title)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True, default=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    
    def __str__(self):
        return str(self.title)


class Cart(models.Model):
    user = models.OneToOneField(CustomUser, related_name="cart", on_delete=models.CASCADE)
    total = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False,)
  
    class Meta:
        verbose_name = _("cart")
        verbose_name_plural = _("carts")
  
    def __str__(self):
        return self.user


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    
    def __str__(self):
        return str(self.menuitem)
    
    class Meta:
        unique_together = ("menuitem", "cart")
    
    def save(self, *args, **kwargs):
        self.price = self.unit_price * self.quantity 
        self.cart.total += self.quantity
        self.cart.save()
        super().save(*args, **kwargs)


class Order(models.Model):
    class StatusChoice(models.TextChoices):
        DELIVERED = "delivered", _("delivered")
        PENDING = "pending", _("pending")
        
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="delivery_crew", null=True)
    status = models.CharField(
        max_length=50,
        choices=StatusChoice.choices, 
        default=StatusChoice.PENDING, 
        db_index=True)
    total = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_updated = models.DateTimeField(auto_now=True)
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    
    class Meta:
        unique_together = ("menuitem", "order")

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = Decimal(self.unit_price * self.quantity )
        # self.order.total += self.quantity
        # self.order.save()
        super().save(*args, **kwargs)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_cart(sender, instance=None, created=False, **kwargs):
    if created:
        Cart.objects.create(user=instance)
