from rest_framework import permissions


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
