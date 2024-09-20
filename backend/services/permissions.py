from rest_framework import permissions

class IsPetOwnerOrReadOnlyOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        # Allow admins to perform any action
        if request.user.is_staff:
            return True
        # Allow authenticated pet owner users to create new objects
        if request.method == 'POST':
            return request.user.is_authenticated and request.user.user_type == "petowner"
        # For other methods, defer to has_object_permission
        return True

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow admins to perform any action
        if request.user.is_staff:
            return True

        # Write permissions are only allowed to the owner of the request.
        return obj.owner == request.user
    
from rest_framework import permissions

from rest_framework import permissions

class IsCaregiverOrReadOnlyOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow:
    - Caregivers to create and edit their own offers
    - Read-only access for other authenticated users
    - Full access for admin users
    """

    def has_permission(self, request, view):
        # Allow read permissions for any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Allow admin users full access
        if request.user.is_staff:
            return True

        # Allow caregivers to create new offers
        if request.method == 'POST':
            return request.user.is_authenticated and request.user.user_type =="caregiver"

        # For other methods, defer to has_object_permission
        return True

    def has_object_permission(self, request, view, obj):
        # Allow read permissions for any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Allow admin users full access
        if request.user.is_staff:
            return True

        # Allow caregivers to edit their own offers
        return request.user.user_type =="caregiver" and obj.caregiver == request.user