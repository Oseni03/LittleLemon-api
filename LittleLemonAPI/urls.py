from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("menu-items", views.MenuItemsView.as_view()),
    path("menu-items/<int:pk>", views.SingleMenuItemView.as_view()),
    path("categories", views.CategoriesView.as_view()),
    path("categories/<int:pk>", views.SingleCategoryView.as_view()),
    path("secrets", views.SecretView.as_view()),
    path("manager-view", views.ManagerView.as_view()),
    path("api-token-auth", obtain_auth_token),
    path("throttle-check", views.ThrottleCheck.as_view()),
    path("throttle-check-auth", views.ThrottleCheckAuth.as_view()),
    path("groups/manager/users", views.ManagerCreateView.as_view()),
]