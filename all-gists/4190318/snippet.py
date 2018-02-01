from django.core.exceptions import PermissionDenied
from django.contrib import admin
from django.contrib.admin.actions import delete_selected as delete_selected_


def delete_selected(modeladmin, request, queryset):
    if not modeladmin.has_delete_permission(request):
        raise PermissionDenied
    if request.POST.get('post'):
        for obj in queryset:
            obj.delete()
    else:
        return delete_selected_(modeladmin, request, queryset)
delete_selected.short_description = "Delete selected objects"


class MyModelAdmin(admin.ModelAdmin):
    actions = [delete_selected]