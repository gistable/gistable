def AbstractClassWithoutFieldsNamed(cls, *excl):
    """
    Removes unwanted fields from abstract base classes.

    Usage::
    >>> from oscar.apps.address.abstract_models import AbstractBillingAddress

    >>> from koe.meta import AbstractClassWithoutFieldsNamed as without
    >>> class BillingAddress(without(AbstractBillingAddress, 'phone_number')):
    ...     pass
    """
    if cls._meta.abstract:
        remove_fields = [f for f in cls._meta.local_fields if f.name in excl]
        for f in remove_fields:
            cls._meta.local_fields.remove(f)
        return cls
    else:
        raise Exception("Not an abstract model")
