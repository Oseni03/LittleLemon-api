from rest_framework import permissions


class IsManager(permissions.BasePermission):
    """
    Manager permission check for authorizing manager only.
    """
    message = "Unauthorized: Managers only view"
    
    def has_permission(self, request, view):
        manager = request.user.groups.filter(name="Manager").exists()
        return manager


class IsCustomer(permissions.BasePermission):
    """
    Customer permission check for authorizing customer only.
    """
    message = "Unauthorized: Customer only view"
    
    def has_permission(self, request, view):
        customer = request.user.groups.filter(name="Customer").exists()
        return customer 


class IsDeliveryCrew(permissions.BasePermission):
    """
    Delivery Crew permission check for authorizing delivery crew only.
    """
    message = "Unauthorized: Delivery crew only view"
    
    def has_permission(self, request, view):
        crew = request.user.groups.filter(name="Delivery Crew").exists()
        return crew


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class CartListPermission(permissions.BasePermission):
    message = "user's cart items only"
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class OrderPermission(permissions.BasePermission):
    message = "customer's order items only"
    
    def has_permission(self, request, view):
        customer = request.user.groups.filter(name="Customer").exists()
        return customer 
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsManagerOrReadOnly(permissions.BasePermission):
    message = "Restricted to managers only"
    
    def has_permission(self, request, view, obj):
        manager = request.user.groups.filter(name="Manager").exists() 
        if not manager:
            return request.method in permissions.SAFE_METHODS
        return manager