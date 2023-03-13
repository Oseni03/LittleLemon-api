from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group

from rest_framework import generics
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.views import APIView
from rest_framework import status 
from rest_framework.decorators import api_view, throttle_classes, action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAdminUser)
from rest_framework.decorators import permission_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from django_filters import rest_framework as filters

from .models import MenuItem, Category, CustomUser, Cart, Order, CartItem, OrderItem
from .serializers import (
    MenuItemSerializer,CartItemSerializer,
    CategorySerializer, UserSerializer, 
    CartSerializer, OrderSerializer,
    GroupNameSerializer, 
    OrderItemSerializer)
from .filters import MenuItemFilter, OrderFilter
from .permissions import (
    IsManager, IsCustomer, IsDeliveryCrew,
    IsManagerOrReadOnly, UserOrManager,
    IsManagerOrCustomer)

# Create your views here.
class UserViewset(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    queryset = CustomUser.objects.prefetch_related("auth_token", "groups").all()
    serializer_class = UserSerializer 
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAdminUser]
        if (self.action == 'list'):
            permission_classes = [IsManager]
        if (self.action == "retrieve"):
            permission_classes = [UserOrManager]
        if (self.action == "create"):
            permission_classes = [IsManager]
        if (self.action == "put"):
            permission_classes = [UserOrManager]
        if (self.action == "delete"):
            permission_classes = [IsManager]
        return [permission() for permission in permission_classes]
    
    @action(
        detail=True, 
        methods=['get', "delete"], 
        url_path='cart', 
        url_name='cart-list',
        permission_classes = [IsCustomer]
    )
    def cart(self, request, pk=None):
        user = self.get_object()
        cart = get_object_or_404(Cart, user=user)
        if request.method == "DELETE":
            CartItem.objects.filter(cart=cart).delete()
            cart.total = 0 
            cart.save()
        serializer = CartSerializer(cart, many=False)
        return Response(serializer.data, status.HTTP_200_OK)
    
    @action(
        detail=True, 
        methods=['get', "post"], 
        url_path='cart/menu', 
        url_name='cart-items-list',
        serializer_class=CartItemSerializer,
        permission_classes=[IsCustomer]
    )
    def cart_items(self, request, pk=None):
        user = self.get_object()
        if request.method == "POST":
            serializer = CartItemSerializer(data=request.data)
            serializer.cart = user.cart
            serializer.is_valid(raise_exception=False)
            serializer.save(cart=user.cart )
            return Response(serializer.data, status.HTTP_201_CREATED)
        else:
            cartitems = CartItem.objects.prefetch_related("menuitem").filter(cart__user=user)
            serializer = CartItemSerializer(cartitems, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
    
    @action(
        detail=True, 
        methods=['get', "put", "delete"], 
        url_path='cart/menu/(?P<item_id>[^/.]+)', 
        url_name='cart-menu-detail',
        serializer_class=CartItemSerializer,
        permission_classes=[IsCustomer]
    )
    def cart_item(self, request, pk=None, item_id=None):
        user = self.get_object()
        cart = get_object_or_404(CartItem, id=item_id, cart__user=user)
        
        if request.method == "PUT":
            serializer = CartItemSerializer(cart, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status.HTTP_202_ACCEPTED)
        if request.method == "DELETE":
            cart.delete()
            return Response({}, status.HTTP_204_NO_CONTENT)
        serializer = CartItemSerializer(cart, many=False)
        return Response(serializer.data, status.HTTP_200_OK)
    
    @action(
        detail=True, 
        methods=['post', "delete"], 
        url_path='group', 
        url_name='group',
        serializer_class=GroupNameSerializer,
        permission_classes=[IsManager]
    )
    def group(self, request, pk=None):
        user = self.get_object()
        print(request.data)
        # group_name = request.data["group"]
        serializer = GroupNameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group_name = serializer.validated_data["name"]
        group = Group.objects.get(name=group_name)
        if request.method == "POST":
            group.user_set.add(user)
        if request.method == "DELETE":
            group.user_set.remove(user)
        return Response({"message": "success"}, status.HTTP_202_ACCEPTED)


class MenuItemsViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = MenuItem.objects.prefetch_related("category").all()
    serializer_class = MenuItemSerializer
    filterset_class = MenuItemFilter 
    permission_classes=[IsManagerOrReadOnly]


class CategoryViewset(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes=[IsManagerOrReadOnly]


class OrderViewset(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
):
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsCustomer]
        if (self.action == 'list'):
            permission_classes = [IsManager|IsCustomer]
        if (self.action == "retrieve"):
            permission_classes = [IsManager|IsCustomer]
        if (self.action == "create"):
            permission_classes = [IsCustomer]
        if (self.action == "put"):
            permission_classes = [IsCustomer]
        if (self.action == "delete"):
            permission_classes = [IsCustomer]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        manager = self.request.user.groups.filter(name="Manager").exists()
        if manager:
            return Order.objects.prefetch_related("items__menuitem__category").all() 
        return Order.objects.prefetch_related("items__menuitem__category").filter(user=self.request.user)
    
    @action(
        detail=True, 
        methods=['post', "get"],
        url_path='items', 
        url_name='items',
        serializer_class=OrderItemSerializer,
    )
    def order_items(self, request, pk=None):
        order = self.get_object()
        if request.method == "POST":
            serializer = OrderItemSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(order=order)
            return Response(serializer.data, status.HTTP_202_ACCEPTED)
        else:
            items = OrderItem.objects.filter(order=order)
            serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data, status.HTTP_200_OK)