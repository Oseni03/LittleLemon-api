from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate

from rest_framework import generics
from rest_framework import mixins
from rest_framework.views import APIView
from rest_framework import status 
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated, IsAdminUser, 
    IsAuthenticatedOrReadOnly,
    AllowAny, DjangoModelPermissions,
    DjangoModelPermissionsOrAnonReadOnly)
from rest_framework.decorators import permission_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.pagination import LimitOffsetPagination

from django_filters import rest_framework as filters

from .models import MenuItem, Category, CustomUser, Cart, Order, CartItem, OrderItem
from .serializers import (
    MenuItemSerializer,CartItemSerializer,
    CategorySerializer, UserSerializer, 
    CartSerializer, OrderSerializer)
from .throttles import TenCallsPerMinute
from .filters import MenuItemFilter
from .permissions import (
    IsManager, IsCustomer, IsDeliveryCrew,
    IsManagerOrReadOnly, OrderPermission,
    CartListPermission)

# Create your views here.
class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.prefetch_related("groups", "auth_token").all()
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer 
    pagination_class = LimitOffsetPagination
    default_limit = 50
    max_limit = 100 
    limit_query_param = "limit"
    offset_query_param = "offset"


class MenuItemsView(
    generics.GenericAPIView, 
    mixins.ListModelMixin, 
    mixins.CreateModelMixin
):
    queryset = MenuItem.objects.select_related("category").all()
    serializer_class = MenuItemSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MenuItemFilter 
    pagination_class = LimitOffsetPagination
    default_limit = 50
    max_limit = 100 
    limit_query_param = "limit"
    offset_query_param = "offset" 
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SingleUserView(
    generics.RetrieveUpdateAPIView,
    generics.DestroyAPIView):
        queryset = CustomUser.objects.prefetch_related("groups", "auth_token").all()
        permission_classes = [IsAdminUser]
        serializer_class = UserSerializer 


class SingleMenuItemView(
    generics.RetrieveUpdateAPIView,
    generics.DestroyAPIView):
        queryset = MenuItem.objects.select_related("category").all()
        serializer_class = MenuItemSerializer 
        permission_classes = [IsManagerOrReadOnly]


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer 


class SingleCategoryView(
    generics.RetrieveUpdateAPIView,
    generics.DestroyAPIView):
        queryset = Category.objects.all()
        serializer_class = CategorySerializer 
        permission_classes = [IsManager]


class GroupView(APIView):
    permission_classes = [IsManager]
    
    def post(self, request, pk):
        user = get_object_or_404(User, id=pk)
        group_name = request.data["group"]
        group = Group.objects.get(name=group_name)
        group.user_set.add(user)
        return Response({"message": f"user added successfully to {group}"})
    
    def put(self, request, pk):
        user = get_object_or_404(User, id=pk)
        group_name = request.data["group"]
        group = Group.objects.get(name=group_name)
        group.user_set.remove(user)
        return Response({"message": f"user removed successfully from {group_name}"})


class CartView(generics.RetrieveAPIView):
    queryset = Cart.objects.select_related("user").prefetch_related("items__menuitem").all()
    serializer_class = CartSerializer 
    lookup_field = "user_id"
    lookup_url_kwarg = "pk"
    permission_classes = [IsCustomer]


class CartItemView(generics.ListCreateAPIView):
    queryset = CartItem.objects.select_related("cart__user").prefetch_related("menuitem").all()
    serializer_class = CartItemSerializer 
    permission_classes = [IsCustomer]
    
    # def post(self, request, *args, **kwargs):
    #     item = self.serializer_class(**request.data)
    #     item.cart=request.user.cart
    #     item.save()
    #     return Response(item.data, status.HTTP_201_CREATED)


class ThrottleCheck(APIView):
    throttle_classes = [AnonRateThrottle]
    
    def get(self, request):
        return Response({"message": "successful"})


class ThrottleCheckAuth(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    def get(self, request):
        return Response({"message": "message for the logged in user only"})


class OrderListCreateView(APIView):
    permission_classes = [OrderPermission]
    serializer_class = OrderSerializer
    
    def get(self, request, *args, **kwargs):
        orders = Order.objects.prefetch_related("items").filter(user=request.user)
        serialized = self.serializer_class(orders, many=True)
        return Response(serialized.data, status.HTTP_200_OK)


class OrderRetrieveUpdateView(
    generics.GenericAPIView, 
    mixins.RetrieveModelMixin, 
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    queryset = Order.objects.prefetch_related("user", "items__menuitem").all()
    permission_classes = [OrderPermission]
    serializer_class = OrderSerializer 
    
    def get(self, request, *args, **kwargs):
        return retrieve(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return destroy(request, *args, **kwargs)