import logging

from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import Unauthorized

from guardian.shortcuts import get_objects_for_user
from guardian.core import ObjectPermissionChecker


logger = logging.getLogger(__name__)


class GuardianAuthorization(DjangoAuthorization):

    """
    :create_permission_code:
        the permission code that signifies the user can create one of these objects
    :view_permission_code:
        the permission code that signifies the user can view the detail
    :update_permission_code:
        the permission code that signifies the user can update one of these objects
    :remove_permission_code:
        the permission code that signifies the user can remove one of these objects

    :kwargs:
        other permission codes


        class Something(models.Model):
            name = models.CharField()

        class SomethingResource(ModelResource):
            class Meta:
                queryset = Something.objects.all()
                authorization = GuardianAuthorization(
                    view_permission_code = 'can_view',
                    create_permission_code = 'can_create',
                    update_permission_code = 'can_update',
                    delete_permission_code = 'can_delete'
                    )

    """

    def __init__(self, *args, **kwargs):
        self.view_permission_code = kwargs.pop("view_permission_code", 'can_view')
        self.create_permission_code = kwargs.pop("create_permission_code", 'can_create')
        self.update_permission_code = kwargs.pop("update_permission_code", 'can_update')
        self.delete_permission_code = kwargs.pop("delete_permission_code", 'can_delete')
        super(GuardianAuthorization, self).__init__(*args, **kwargs)

    def generic_base_check(self, object_list, bundle):
        """
            Returns False if either:
                a) if the `object_list.model` doesn't have a `_meta` attribute
                b) the `bundle.request` object doesn have a `user` attribute
        """
        klass = self.base_checks(bundle.request, object_list.model)
        if klass is False:
            raise Unauthorized("You are not allowed to access that resource.")
        return True

    def generic_item_check(self, object_list, bundle, permission):
        if not self.generic_base_check(object_list, bundle):
            raise Unauthorized("You are not allowed to access that resource.")

        checker = ObjectPermissionChecker(bundle.request.user)
        if not checker.has_perm(permission, bundle.obj):
            raise Unauthorized("You are not allowed to access that resource.")

        return True

    def generic_list_check(self, object_list, bundle, permission):
        if not self.generic_base_check(object_list, bundle):
            raise Unauthorized("You are not allowed to access that resource.")

        return get_objects_for_user(bundle.request.user, object_list, permission)

    # List Checks
    def create_list(self, object_list, bundle):
        return self.generic_list_check(object_list, bundle,
            self.create_permission_code)

    def read_list(self, object_list, bundle):
        return self.generic_list_check(object_list, bundle,
            self.view_permission_code)

    def update_list(self, object_list, bundle):
        return self.generic_list_check(object_list, bundle,
            self.update_permission_code)

    def delete_list(self, object_list, bundle):
        return self.generic_list_check(object_list, bundle,
            self.delete_permission_code)

    # Item Checks
    def create_detail(self, object_list, bundle):
        return self.generic_item_check(object_list, bundle,
            self.create_permission_code)

    def read_detail(self, object_list, bundle):
        return self.generic_item_check(object_list, bundle,
            self.view_permission_code)

    def update_detail(self, object_list, bundle):
        return self.generic_item_check(object_list, bundle,
            self.update_permission_code)

    def delete_detail(self, object_list, bundle):
        return self.generic_item_check(object_list, bundle,
            self.delete_permission_code)

