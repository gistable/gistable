from django.contrib import admin                                                                            
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from userprofiles.models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'
    max_num = 1

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "delegates_mrm":
            kwargs["queryset"] = User.objects.extra(
                    tables=['userprofiles_userprofile'],
                    where=['"auth_user"."id"="userprofiles_userprofile"."user_id"'],
                    select={'is_report':'"userprofiles_userprofile"."manager_id"=%s' % request.user.id}     
                ).order_by('-is_report', 'username')
        return super(UserProfileInline, self).formfield_for_manytomany(db_field, request, **kwargs)


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline,]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
