from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User, Group

from rest_framework import generics
from rest_framework import status 
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from .models import MenuItem, Category 
from .serializers import MenuItemSerializer, CategorySerializer
from .throttles import TenCallsPerMinute

# Create your views here.
@api_view(["GET", "POST"])
def menu_items(request):
    if request.method == "GET":
        items = MenuItem.objects.all()
        category_name = request.query_params.get("category")
        to_price = request.query_params.get("to_price")
        search = request.query_params.get("search")
        ordering = request.query_params.get("ordering")
        perpage = request.query_params.get("perpage", default=2)
        page = request.query_params.get("page", default=1)
        if category_name:
            items = items.filter(category__slug=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__icontains=search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)
            
        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data)
    elif request.method == "POST":
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status.HTTP_201_CREATED)


@api_view()
def single_item(request, pk):
    item = get_object_or_404(MenuItem, id=pk)
    serialized_item = MenuItemSerializer(item)
    return Response(serialized_item.data)


@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({"message": "some secret message"})


@api_view()
@permission_classes([IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter(name="Manager").exists():
        return Response({"message": "Only manager is allowed to see this"})
    else:
        return Response({"message": "You are not authorized"}, 403)


@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({"message": "successful"})


@api_view()
@throttle_classes([UserRateThrottle])
@permission_classes([IsAuthenticated])
def throttle_check_auth(request):
    return Response({"message": "message for the logged in user only"})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data["username"]
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        if request.method == "POST":
            managers.user_set.add(user)
        elif request.method == "DELETE":
            managers.user_set.remove(user)
        return Response({"message": "ok"})
    return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.select_related("category").all()
    serializer_class = MenuItemSerializer


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SingleCategoryView(
    generics.RetrieveUpdateAPIView,
    generics.DestroyAPIView):
        queryset = Category.objects.all()
        serializer_class = CategorySerializer


class SingleMenuItemView(
    generics.RetrieveUpdateAPIView,
    generics.DestroyAPIView):
        queryset = MenuItem.objects.all()
        serializer_class = MenuItemSerializer