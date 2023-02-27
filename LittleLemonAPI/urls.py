from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path("menu-items", views.MenuItemsView.as_view()),
    # path("menu-items/<int:pk>", views.SingleMenuItemView.as_view()),
    path("categories", views.CategoriesView.as_view()),
    path("categories/<int:pk>", views.SingleCategoryView.as_view()),
    
    path("menu-items", views.menu_items),
    path("menu-items/<int:pk>", views.single_item),
    path("secrets", views.secret),
    path("manager-view", views.manager_view),
    path("api-token-auth", obtain_auth_token),
    path("throttle-check", views.throttle_check),
    path("throttle-check-auth", views.throttle_check_auth),
    path("groups/manager/users", views.managers),
]