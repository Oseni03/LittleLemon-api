from rest_framework import permissions

class IsManager(permissions.BasePermission):
    """
    manager permission check for authorizing manager only.
    """
    message = "Unauthorized: managers only view"
    
    def has_permission(self, request, view):
        manager = request.user.groups.filter(name="Manager").exists()
        return manager