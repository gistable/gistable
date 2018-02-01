from django.db.models.query import QuerySet
from django.db import models


class QuerySetManager(QuerySet):
    '''
    Subclass this class to define custom Managers with chainable, custom
    QuerySet calls. 

    For example, define your queryset subclassing this object:
    
        class MyModelQuerySet(QuerySetManager):
            
            def active(self):
                return self.filter(active=True)

            def published(self):
                return self.filter(published=True)
         
    In your model definition, set the `objects` attribute as follows:

        class MyModel(models.Model):
            active = models.BooleanField()
            published = models.BooleanField()

            # Here is the usage
            objects = MyModelQuerySet().as_manager()
 
    Which allows calls like:

        >> MyModel.objects.active().published()

    This is intended to avoid the boilerplate of the common technique
    described here:
        http://djangosnippets.org/snippets/734/
        http://seanmonstar.com/post/708862164/extending-django-models-managers-and-querysets
    '''
    def as_manager(self):

        qs_class = self.__class__

        class Manager(models.Manager):

            # https://docs.djangoproject.com/en/dev/topics/db/managers/#controlling-automatic-manager-types
            use_for_related_fields = True

            def get_query_set(self):
                return qs_class(self.model)

            def __getattr__(self, attr, *args):
                # Avoids recursive copy when using proxy models, see: 
                #   https://code.djangoproject.com/ticket/15062
                #   https://docs.djangoproject.com/en/dev/topics/db/managers/#implementation-concerns
                #   http://nedbatchelder.com/blog/201010/surprising_getattr_recursion.html 
                if attr.startswith("__"):
                    raise AttributeError
                try:
                    return getattr(self.__class__, attr, *args)
                except AttributeError:
                    return getattr(self.get_query_set(), attr, *args) 
        return Manager()
