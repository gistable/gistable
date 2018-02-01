# Based on post from: https://snipt.net/chrisdpratt/symmetrical-manytomany-filter-horizontal-in-django-admin/#L-26
# Only reposting to avoid loosing it.

"""
When adding a many-to-many (m2m) relationship in Django, you can use a nice filter-style multiple select widget to manage entries. However, Django only lets you edit the m2m relationship this way on the forward model. The only built-in method in Django to edit the reverse relationship in the admin is through an InlineModelAdmin.

Below is an example of how to create a filtered multiple select for the reverse relationship, so that editing entries is as easy as in the forward direction.
"""

### pizza/models.py ###

from django.db import models

class Pizza(models.Model):
  name = models.CharField(max_length=50)
  toppings = models.ManyToManyField(Topping, related_name='pizzas')

class Topping(models.Model):
  name = models.CharField(max_length=50)

### pizza/admin.py ###

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import Pizza, Topping

class PizzaAdmin(admin.ModelAdmin):
  filter_horizonal = ('toppings',)

class ToppingAdminForm(forms.ModelForm):
  pizzas = forms.ModelMultipleChoiceField(
    queryset=Pizza.objects.all(), 
    required=False,
    widget=FilteredSelectMultiple(
      verbose_name=_('Pizzas'),
      is_stacked=False
    )
  )

  class Meta:
    model = Topping

  def __init__(self, *args, **kwargs):
    super(ToppingAdminForm, self).__init__(*args, **kwargs)

    if self.instance and self.instance.pk:
      self.fields['pizzas'].initial = self.instance.pizzas.all()

  def save(self, commit=True):
    topping = super(ToppingAdminForm, self).save(commit=False)

    if commit:
      topping.save()

    if topping.pk:
      topping.pizzas = self.cleaned_data['pizzas']
      self.save_m2m()

    return topping

class ToppingAdmin(admin.ModelAdmin):
  form = ToppingAdminForm

admin.site.register(Pizza, PizzaAdmin)
admin.site.register(Topping, ToppingAdmin)