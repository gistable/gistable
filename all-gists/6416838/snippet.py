def get_cache_key(model, pk):
    """
    Generates a cache key based on ``WRITE_CACHE_PREFIX``, the cache key prefix
    defined in the settings file (if any), the Django app and model name, and
    the primary key of the object.
    """
    params = {
        'prefix': getattr(settings, 'WRITE_CACHE_PREFIX', ''),
        'app': model._meta.app_label,
        'model': model._meta.object_name,
        'pk': pk,
    }
    return '{prefix}django-write-cache-{app}.{model}-pk={pk}'.format(**params)


def get_from_cache(model, pk):
    """
    Retrieves an object from the cache for the given model class and primary
    key.
    """
    key = get_cache_key(model, pk)
    return cache.get(key)


def add_to_cache(obj):
    """
    Adds the given object to the cache, with a key based on its primary key.
    """
    key = get_cache_key(obj.__class__, obj.pk)
    timeout = getattr(settings, 'WRITE_CACHE_TIMEOUT', 3600)
    cache.set(key, obj, timeout)


def update_write_cache(func):
    """
    Decorator for model save() methods that should update the write-through
    cache upon completion.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        r = func(self, *args, **kwargs)
        add_to_cache(self)
        return r
    return wrapper


class WriteCacheQuerySet(models.query.QuerySet):
    """
    Simple queryset that hijacks the .get() method to return a cached
    version of the object based on the primary key, if available.
    """

    def get(self, *args, **kwargs):
        obj = None
        cachable = not args and (kwargs.keys() == ['pk'] or
                                 kwargs.keys() == ['id'])
        if cachable:
            obj = get_from_cache(self.model, kwargs.values()[0])
        if obj is None:
            obj = super(WriteCacheQuerySet, self).get(*args, **kwargs)
            if cachable:
                add_to_cache(obj)
        return obj

    def update(self, **kwargs):
        raise NotImplementedError('update() does not yet support updating the '
                                  'write-through cache.')


class WriteCacheManager(models.Manager):
    """
    Caching manager that returns a WriteCacheQuerySet for calls to
    get_query_set().
    """
    use_for_related_fields = True

    def get_query_set(self):
        return WriteCacheQuerySet(self.model)
