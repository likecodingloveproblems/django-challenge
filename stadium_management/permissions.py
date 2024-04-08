from rest_framework import permissions

from stadium_management.models import Seat


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    It's used for views that all users can view, admins can modify
    """

    def has_permission(self, request, view) -> bool:
        """
        Check request is safe or user is admin
        :param request: the request object
        :type request: HttpRequest
        :param view: django view
        :type view: django.views.View
        :return: user has permission to this operation
        :rtype: bool
        """
        return request.method in permissions.SAFE_METHODS or (
            request.user and request.user.is_staff
        )


class IsAdminAndNotReservedOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Seat):
        """
        Check request is safe or user is admin and seat is not reserved
        :param request: the request object
        :type request: Request
        :param view: view object
        :type view: View
        :param obj: seat object
        :type obj: Seat
        :return: user has permission to this operation
        :rtype: bool
        """
        return request.method in permissions.SAFE_METHODS or (
            request.user and request.user.is_staff and not obj.is_reserved
        )
