"""
Hide permission in the Django admin which are irrelevant, and not used at all.
"""
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User


class PermissionFilterMixin(object):
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in ('permissions', 'user_permissions'):
            qs = kwargs.get('queryset', db_field.rel.to.objects)
            qs = _filter_permissions(qs)
            kwargs['queryset'] = qs

        return super(PermissionFilterMixin, self).formfield_for_manytomany(db_field, request, **kwargs)

class MyGroupAdmin(PermissionFilterMixin, GroupAdmin):
    pass

class MyUserAdmin(PermissionFilterMixin, UserAdmin):
    pass

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, MyUserAdmin)
admin.site.register(Group, MyGroupAdmin)


def _filter_permissions(qs):
    return qs.exclude(codename__in=(
        # Has no admin interface:
        'add_permission',
        'change_permission',
        'delete_permission',

        'add_contenttype',
        'change_contenttype',
        'delete_contenttype',

        'add_session',
        'delete_session',
        'change_session',

        # django.contrib.admin
        'add_logentry',
        'change_logentry',
        'delete_logentry',

        # sorl-thumbnail    
        'add_kvstore',
        'change_kvstore',
        'delete_kvstore',

        # south
        'add_migrationhistory',
        'change_migrationhistory',
        'delete_migrationhistory',

        # django-admin-tools    
        'add_dashboardpreferences',
        'change_dashboardpreferences',
        'delete_dashboardpreferences',

        'add_bookmark',
        'change_bookmark',
        'delete_bookmark',
    )) \
    .exclude(codename__endswith='userobjectpermission') \
    .exclude(codename__endswith='groupobjectpermission')  # django-guardian
