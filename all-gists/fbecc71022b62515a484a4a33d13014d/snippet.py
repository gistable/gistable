"""
Logical deletion for Django models. Uses is_void flag
to hide discarded items from queries. Overrides delete
methods to set flag and soft-delete instead of removing
rows from the database.
"""
from django.apps import apps
from django.contrib.admin.utils import NestedObjects
from django.db import models
from django.db.models import signals

class DeleteNotPermitted(Exception):
    pass

class ObjectIsVoid(models.ObjectDoesNotExist):
    pass

class AppQuerySet(models.QuerySet):
    def _wrap(self, func, args, kwargs):
        """
        If an object doesn't exist, check to see if it exists. If it doesn't, remove the
        `is_void` filter and raise IsVoid exception if found.
        """
        try:
            r = func(*args, **kwargs)
        except self.model.DoesNotExist, e:
            for node in self.query.where.children[:]:
                if hasattr(node, 'children'):
                    for child in node.children:
                        if child.lhs.target.attname == 'is_void':
                            node.children.remove(child)
                    if not node.children:
                        self.query.where.children.remove(node)
            q = super(AppQuerySet, self).filter(*args, **kwargs)
            if q.exists():
                raise self.model.IsVoid('Object exists but is void.')
            else:
                raise e
        return r

    def get(self, *args, **kwargs):
        return self._wrap(
            super(AppQuerySet, self).get, args, kwargs
        )

    def get_or_create(self, *args, **kwargs):
        return self._wrap(
            super(AppQuerySet, self).get_or_create, args, kwargs
        )

    def delete(self, cascade=True, **kwargs):
        if self.model.PREVENT_DELETE:
            raise DeleteNotPermitted()
        if cascade:
            for obj in self.all():
                obj.delete()
        else:
            return self.update(is_void=True)

class AppManager(models.Manager):
    queryset_class = AppQuerySet
    use_for_related_fields = True

    def get_queryset(self, exclude_void=True):
        q = self.queryset_class(self.model)
        if hasattr(self, 'core_filters'):
            q = q.filter(
                **self.core_filters
            )

        if exclude_void:
            q = q.exclude(is_void=True)
        return q

    def all_objects_including_void(self):
        return self.get_queryset(exclude_void=False)

class AppModelMeta(type(models.Model)):
    def __new__(cls, name, parents, dct):
        new_class = super(AppModelMeta, cls).__new__(cls, name, parents, dct)
        if hasattr(new_class, 'DoesNotExist'):
            new_class.IsVoid = type('IsVoid', (new_class.DoesNotExist, ObjectIsVoid), {})
        return new_class

class AppModel(models.Model):
    __metaclass__ = AppModelMeta

    PREVENT_DELETE = False
    is_void = models.BooleanField(default=False)
    objects = AppManager()

    class Meta:
        abstract = True

    def delete(self, cascade=True, **kwargs):
        if self.PREVENT_DELETE:
            raise DeleteNotPermitted()

        if cascade:
            collector = NestedObjects(using='default')
            collector.collect([self])
            field_updates = collector.field_updates
            for cls, to_update in field_updates.iteritems():
                for (field, value), instances in to_update.iteritems():
                    cls.objects.filter(
                        pk__in={o.pk for o in instances}
                    ).update(
                        **{field.attname: value}
                    )
            for klass, objs in collector.data.iteritems():
                try:
                    klass._meta.get_field('is_void')
                except models.FieldDoesNotExist:
                    pass
                else:
                    klass.objects.filter(pk__in={o.pk for o in objs}).update(
                        is_void=True
                    )
        else:
            self.is_void = True
            self.save()
        signals.post_delete.send(
            sender=self.__class__, instance=self
        )