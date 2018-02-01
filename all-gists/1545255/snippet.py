""" User Django Rest Framework to check to see if an authenticated user 
is in a particular group

Usage::

    from api.group_permissions import GroupAPIGETPermission
    class SearchProductView(View):
    
        permissions = (IsAuthenticated, GroupAPIGETPermission,)    

"""

from django.contrib.auth.models import Group

from djangorestframework.permissions import _403_FORBIDDEN_RESPONSE, BasePermission

class GroupBasePermission(BasePermission):
    
    group_name = ""
    
    def check_permission(self, user):
        """
        Should simply return, or raise a 403 response.
        """
        try:
            user.groups.get(name=self.group_name)    
        except Group.DoesNotExist:
            raise _403_FORBIDDEN_RESPONSE

class GroupAPIGETPermission(GroupBasePermission):
    """
        Checks to see if a user is in a particular group
    """
    
    group_name = "API GET"
    
class GroupAPIPOSTPermission(GroupBasePermission):
    """
        Checks to see if a user is in a particular group
    """

    group_name = "API POST"    