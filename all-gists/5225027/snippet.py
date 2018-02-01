from django.contrib import admin
import reversion
from mezzanine.pages.admin import PageAdmin
from mezzanine.pages.models import Page

class NewPageAdmin(PageAdmin, reversion.VersionAdmin):
    pass

admin.site.unregister(Page)
admin.site.register(Page, NewPageAdmin)