'''
Taken from: https://code.djangoproject.com/ticket/17561#comment:7
'''

from django.db import models


class EmailField(models.EmailField):
    def get_prep_value(self, value):
        value = super(EmailField, self).get_prep_value(value)
        if value is not None:
            value = value.lower()
        return value