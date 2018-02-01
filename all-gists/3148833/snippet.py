from django.db import models
from django.db.models import Manager
from django.db.models.query import QuerySet

class CaseInsensitiveQuerySet(QuerySet):
  def _filter_or_exclude(self, mapper, *args, **kwargs):
  # 'name' is a field in your Model whose lookups you want case-insensitive by default
    if 'name' in kwargs:
      kwargs['name__iexact'] = kwargs['name']
      del kwargs['name']
    return super(CaseInsensitiveQuerySet, self)._filter_or_exclude(mapper, *args, **kwargs)
# custom manager that overrides the initial query set
class BrandManager(Manager):
  def get_query_set(self):
    return CaseInsensitiveQuerySet(self.model)
# and the model itself
class Brand(models.Model):
  name = models.CharField(max_length=50, unique=True, db_index=True)
  objects = BrandManager()
  def __str__(self):
    return self.name  