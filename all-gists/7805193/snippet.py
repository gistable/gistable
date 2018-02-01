from django.contrib.gis.db import models
from django.contrib.gis.db.models.query import GeoQuerySet
from polymorphic import PolymorphicManager
from polymorphic.query import PolymorphicQuerySet


class GeoPolymorphicQuerySet(GeoQuerySet, PolymorphicQuerySet):
    '''
    QuerySet used in GeoPolymorphicManager.
    '''
    pass


class GeoPolymorphicManager(models.GeoManager, PolymorphicManager):
    '''
    GeoManager with polymorfism functionalities (for django-polymorphic).
    '''
    queryset_class = GeoPolymorphicQuerySet

    def get_query_set(self):
        return self.queryset_class(self.model, using=self._db)