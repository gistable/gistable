from django.db.models.query import EmptyQuerySet

class FakeQuerySet(EmptyQuerySet):
    """Turn a list into a Django QuerySet... kind of."""
    def __init__(self, model=None, query=None, using=None, items=[]):
        super(FakeQuerySet, self).__init__(model, query, using)
        self._result_cache = items

    def count(self):
        return len(self)
