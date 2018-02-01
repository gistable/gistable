"""
You find yourself doing this all the time?

    >>> car = Car.objects.get(id=1)
    >>> if c.user != request.user:
    >>>     return HttpResponse("This car doesn't belong to you")
    >>> c.brand = request.POST.get('brand_name')
    >>> c.save()

Better to turn it into:

    >>> try:
    >>>     with ensure_instance_owner(car, user) as c:
    >>>         c.brand = request.POST.get('brand_name')
    >>> except NotInstanceOwner:
    >>>     return HttpResponse("This car doesn't belong to you")

"""
class NotInstanceOwner(Exception):
    pass


class EnsureModelInstanceOwner(object):
    def __init__(self, instance, user, owner_field='user'):
        self.instance = instance
        self.owner_field = owner_field
        self.user = user

    def __enter__(self):
        owner = getattr(self.instance, self.owner_field)
        if owner != self.user:
            raise NotInstanceOwner()
        return self.instance

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.instance.save()

ensure_instance_owner = EnsureModelInstanceOwner

"""
Now, I  don't like that Car.objects.get, let's make it better:

    >>> try:
    >>>     with get_and_ensure_owner(Car, 1, user) as c:
    >>>         c.brand = request.POST.get('brand_name')
    >>> except Car.DoesNotExist:
    >>>     return HttpResponseNotFound()
    >>> except NotInstanceOwner:
    >>>     return HttpResponse("This car doesn't belong to you")

"""

class GetAndEnsureOwner(object):
    def __init__(self, model_class, pk, user, owner_field='user'):
        self.model_class = model_class
        self.pk = pk
        self.owner_field = owner_field
        self.user = user

    def __enter__(self):
        self.instance = self.model_class.objects.get(pk=self.pk)
        owner = getattr(self.instance, self.owner_field)
        if owner != self.user:
            raise NotInstanceOwnerException()
        return self.instance

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.instance.save()

get_and_ensure_owner = GetAndEnsureOwner

# License: DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE