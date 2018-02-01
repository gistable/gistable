from __future__ import unicode_literals

from django.db import models
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor  # noqa


class RelationNotLoaded(Exception):
    pass


class StrictForwardManyToOne(ForwardManyToOneDescriptor):
    def __get__(self, instance, cls=None):
        try:
            return getattr(instance, self.cache_name)
        except AttributeError:
            raise RelationNotLoaded(
                'Relation `{rel}` not loaded. Use `select_related` or '
                '`fetch_{rel}`'.format(rel=self.field.name)
            )

    def explicit_get(self, instance, cls=None):
        return super(StrictForwardManyToOne, self).__get__(instance, cls)


class StrictForeignKey(models.ForeignKey):

    def contribute_to_class(self, cls, name, **kwargs):
        super(StrictForeignKey, self).contribute_to_class(cls, name, **kwargs)
        #  Override the descriptor defined by ForeignObject
        descriptor = StrictForwardManyToOne(self)
        setattr(cls, self.name, descriptor)
        #  Add a method so you don't always have to use select_related
        fetch_name = 'fetch_{rel}'.format(rel=self.name)
        setattr(cls, fetch_name, lambda inst: descriptor.explicit_get(inst))


# Create your models here.
class Author(models.Model):
    name = models.TextField()


class Book(models.Model):
    title = models.TextField()
    author = StrictForeignKey(Author, on_delete=models.PROTECT, related_name='books')
