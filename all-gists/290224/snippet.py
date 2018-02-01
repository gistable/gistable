from django.contrib.admin import widgets
from django import forms
from django.contrib import admin

# create wrappers for overriding the queryset

class ToWrapper(object):
    def __init__(self, to, manager):
        self.to = to
        self._default_manager = manager

    def __getattr__(self, name):
        return getattr(self.to, name)

class RelWrapper(object):
    def __init__(self, rel, manager):
        self.rel = rel
        self.to = ToWrapper(rel.to, manager)

    def __getattr__(self, name):
        return getattr(self.rel, name)

class FooForm(forms.ModelForm):
    bar = forms.ModelChoiceField(queryset=Bar.all_objects,
            label=_("Bar"),
            widget=widgets.ForeignKeyRawIdWidget(
                RelWrapper(Foo._meta.get_field('bar').rel,
                    Bar.all_objects)))

    class Meta:
        model = Foo

class FooAdmin(admin.ModelAdmin):
    form = FooForm