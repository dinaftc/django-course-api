from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='manager').exists()

class IsDeliveryBoy(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Delivery crew').exists()

class IsSuperAdminOrManagerOrReadOnly(BasePermission):
    """
    Custom permission to only allow superadmin and manager to edit objects,
    while allowing read-only access for other authenticated users (customers).
    """
    def has_permission(self, request, view):
        # Allow read-only permissions for any authenticated user
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        
        # Allow full access to superadmin and manager
        return (
            request.user.is_authenticated and 
            (request.user.groups.filter(name='superadmin').exists() or
             request.user.groups.filter(name='manager').exists())
        )
