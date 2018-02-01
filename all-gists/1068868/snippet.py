"""
Example of installing django-taggit onto a Zinnia Entry model
(django-blog-zinnia) which traditionally uses django-tagging.

The django-taggit manager is installed on the tagged_as attribute because
tagged is already taken by the existing django-tagging installation (which we don't remove).

"""

from django.contrib import admin
from django.db import models
from django.db.models import get_model
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from taggit.forms import TagField

# you don't need to use the taggit_autocomplete library if you don't want.
# instead use taggit.managers.TaggableManager
from taggit_autocomplete.managers import TaggableManager
from taggit_autocomplete.widgets import TagAutocomplete

from zinnia.admin import entry
from zinnia.admin.forms import EntryAdminForm

class TaggitModel(models.Model):
    tagged_as = TaggableManager()

    class Meta:
        abstract = True

class TaggitEntryForm(EntryAdminForm):

    tagged_as = TagField(widget=TagAutocomplete)
    def __init__(self, *args, **kwargs):
        super(TaggitEntryForm, self).__init__(*args, **kwargs)

class TaggitZinniaEntry(get_model('zinnia','entry'), TaggitModel):
    """
    A Zinnia entry that uses django taggit instead of django-tagging ugh!

    """

    class Meta:
        proxy = True
        verbose_name = _("Entry")
        verbose_name_plural = _("Entries")


    def save(self):
        """
        Put the taggit tags into the django-tagging field. So they are in sync.

        """
        if not self.slug:
            self.slug = slugify(self.title)

        super(TaggitZinniaEntry, self).save()

# monkey patch zinnia to use this entry instead.
models.Entry = TaggitZinniaEntry

class MyZinniaAdmin(entry.EntryAdmin):
    """
    Zinnia admin shows a tagged_as field (to avoid clash with tagged), which has the taggit manager.

    """
    form = TaggitEntryForm


# now install our shiny new zinnia-entry into the admin.
admin.site.unregister(get_model('zinnia', 'entry'))
admin.site.register(TaggitZinniaEntry, MyZinniaAdmin)

# all done?! Not so fast, you might want to install some signals that keep tagging and taggit in sync 
# if keeping them in sync is important to you.