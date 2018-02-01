from django.db.models.manager import Manager


class PassThroughManager(Manager):
    '''
    Inherit from this Manager to enable you to call any methods from your
    custom QuerySet class from your manager. Simply define your QuerySet
    class, and return an instance of it from your manager's `get_query_set`
    method.
    
    Alternately, if you don't need any extra methods on your manager that
    aren't on your QuerySet, then just pass your QuerySet class to this
    class' constructer.
    
    class PostQuerySet(QuerySet):
        def enabled(self):
            return self.filter(disabled=False)
    
    class Post(models.Model):
        objects = PassThroughManager(PostQuerySet)
    '''
    # pickling causes recursion errors
    _deny_methods = ['__getstate__', '__setstate__']
    
    def __init__(self, queryset_cls=None):
        self._queryset_cls = queryset_cls
        super(PassThroughManager, self).__init__()
    
    def __getattr__(self, name):
        if name in self._deny_methods:
            raise AttributeError(name)
        return getattr(self.get_query_set(), name)
    
    def get_query_set(self):
        if self._queryset_cls is not None:
            return self._queryset_cls(self.model, using=self._db)
        return super(PassThroughManager, self).get_query_set()