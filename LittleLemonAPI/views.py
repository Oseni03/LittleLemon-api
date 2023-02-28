from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User, Group

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status 
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.pagination import LimitOffsetPagination

from django_filters import rest_framework as filters

from .models import MenuItem, Category 
from .serializers import MenuItemSerializer, CategorySerializer
from .throttles import TenCallsPerMinute
from .filters import MenuItemFilter
from .permissions import IsManager

# Create your views here.
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.select_related("category").all()
    serializer_class = MenuItemSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MenuItemFilter 
    pagination_class = LimitOffsetPagination
    default_limit = 50
    max_limit = 100 
    limit_query_param = "limit"
    offset_query_param = "offset"


class SingleMenuItemView(
    generics.RetrieveUpdateAPIView,
    generics.DestroyAPIView):
        queryset = MenuItem.objects.all()
        serializer_class = MenuItemSerializer


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SingleCategoryView(
    generics.RetrieveUpdateAPIView,
    generics.DestroyAPIView):
        queryset = Category.objects.all()
        serializer_class = CategorySerializer


class SecretView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({"message": "some secret message"})


class ManagerCreateView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        username = request.data["username"]
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="Manager")
            managers.user_set.add(user)
            return Response({"message": "ok"})
        return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        username = request.data["username"]
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="Manager")
            managers.user_set.remove(user)
            return Response({"message": "ok"})
        return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)


class ManagerView(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    
    def get(self, request):
        return Response({"message": "Success"}) 


class ThrottleCheck(APIView):
    throttle_classes = [AnonRateThrottle]
    
    def get(self, request):
        return Response({"message": "successful"})


class ThrottleCheckAuth(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    def get(self, request):
        return Response({"message": "message for the logged in user only"})