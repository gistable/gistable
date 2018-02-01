from rest_framework.permissions import BasePermission


class IsAjaxPermission(BasePermission):
    """
    Check is request is ajax.
    """

    def has_object_permission(self, request, view, obj):
        return request.is_ajax()

    def has_permission(self, request, view):
        return request.is_ajax()


# if you want to fake it, just put in the request header 'HTTP_X_REQUESTED_WITH'='XMLHttpRequest'

# from django.http.request.py

# def is_ajax(self):
#   return self.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
