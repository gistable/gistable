
# based on http://stackoverflow.com/questions/6459616/overriding-queryset-delete-in-django

class DeactivateQuerySet(models.query.QuerySet):
    '''
    QuerySet whose delete() does not delete items, but instead marks the
    rows as not active, and updates the timestamps
    '''
    def delete(self):
        self.deactivate()

    def deactivate(self):
        deleted = now()
        self.update(active=False, modified=deleted, deleted=deleted)

    def active(self):
        return self.filter(active=True)


class DeactivateManager(models.Manager):
    '''
    Manager that returns a DeactivateQuerySet,
    to prevent object deletion.
    '''
    def get_query_set(self):
        return DeactivateQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_query_set().active()


class DeactivateMixin(models.Model):
    '''
    abstract class for models whose rows should not be deleted but
    items should be 'deactivated' instead.

    note: needs to be the first abstract class for the default objects
    manager to be replaced on the subclass.
    '''
    active = models.BooleanField(default=True, editable=False, db_index=True)
    deleted = models.DateTimeField(default=None, editable=False, null=True)
    objects = DeactivateManager()

    class Meta:
        abstract = True

