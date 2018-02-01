from functools import wraps
from django.core.exceptions import PermissionDenied


def superuser_required(method):
    """
    Decorator to check whether user is super user or not
    If user is not a super-user, it will raise PermissionDenied or
    403 Forbidden.
    """
    @wraps(method)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser is False:
            raise PermissionDenied

        return method(request, *args, **kwargs)

    return _wrapped_view