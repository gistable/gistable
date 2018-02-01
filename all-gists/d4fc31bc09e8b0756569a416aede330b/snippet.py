from django.db import models
from django.core.cache import cache

class SingletonModel(models.Model):

        class Meta:
                abstract = True

        def delete(self, *args, **kwargs):
                pass
                
        def set_cache(self):
                cache.set(self.__class__.__name__, self)

        def save(self, *args, **kwargs):
                self.pk = 1
                super(SingletonModel, self).save(*args, **kwargs)
                self.set_cache()
        
        @classmethod
        def load(cls):
                if cache.get(self.__class__.__name__) is None:
                        obj, created = cls.objects.get_or_create(pk=1)
                        if not created:
                                obj.set_cache()
                return cache.get(self.__class__.__name__)