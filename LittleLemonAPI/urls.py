from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("users", views.UserListCreateView.as_view()),
    path("users/<int:pk>", views.SingleUserView.as_view()),
    path("users/<int:pk>/groups", views.GroupView.as_view()),
    path("users/<int:pk>/cart", views.CartView.as_view()),
    path("users/<int:pk>/cart/menu-items", views.CartItemView.as_view()),
    path("menu-items", views.MenuItemsView.as_view()),
    path("menu-items/<int:pk>", views.SingleMenuItemView.as_view()),
    path("categories", views.CategoriesView.as_view()),
    path("categories/<int:pk>", views.SingleCategoryView.as_view()),
    path("orders", views.OrderListCreateView.as_view()),
    path("orders/<int:pk>/menu-items", views.OrderListCreateView.as_view()),
    path("api-token-auth", obtain_auth_token),
    path("throttle-check", views.ThrottleCheck.as_view()),
    path("throttle-check-auth", views.ThrottleCheckAuth.as_view()),
]