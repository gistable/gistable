from django.contrib.sites.models import Site


class Object(object):
    def __init__(self, model, key):
        self.model = model
        self.key = key

    def __call__(self, *args, **kwargs):
        params = {}
        params[self.key] = args[0]
        return self.model.objects.get(**params)

class Repository(object):
    def __init__(self, model):
        self.model = model

    def get_by_param(self, key):
        return Object(self.model, key)

    def __getattr__(self, key):
        _key = key.replace('get_by_', '')
        return self.get_by_param(_key)


SiteRepository = Repository(Site)

print SiteRepository.get_by_id(1)
