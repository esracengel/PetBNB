from rest_framework import permissions
from services.models import Service

class CanCreateReview(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            service_id = request.data.get('service')
            if not service_id:
                return False
            service = Service.objects.filter(id=service_id).first()
            if not service:
                return False
            return service.is_user_involved(request.user)
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user == obj.reviewer or request.user == obj.reviewee
        return request.user == obj.reviewer