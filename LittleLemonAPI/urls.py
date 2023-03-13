from django.urls import path, include
from rest_framework import routers
from . import views

from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter(trailing_slash=False)
router.register("users", views.UserViewset, basename="user")
router.register("menu", views.MenuItemsViewSet, basename="menu")
router.register("categories", views.CategoryViewset, basename="category")
router.register("orders", views.OrderViewset, basename="order")

urlpatterns = [
    path('', include(router.urls)),
    path("api-token-auth", obtain_auth_token),
]
