from django.db import models

optional = dict(blank=True, null=True)

class Foo(models.Model):
    bar = models.CharField()
    baz = models.CharField(**optional)
