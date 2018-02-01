from itertools import chain
from django.db.models.fields.related import ManyToManyField

def model_to_dict_verbose(instance, fields=None, exclude=None):
    """
    Returns a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument. Keys in dict are exchanged for
    verbose names contained in the model.
    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned dict.
    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned dict, even if they are listed in
    the ``fields`` argument.
    """
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.virtual_fields, opts.many_to_many):
        if not getattr(f, 'editable', False):
            continue
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        verbose_name = opts.get_field(f.name).verbose_name
        if isinstance(f, ManyToManyField):
            # If the object doesn't have a primary key yet, just use an empty
            # list for its m2m fields. Calling f.value_from_object will raise
            # an exception.
            if instance.pk is None:
                data[verbose_name] = []
            else:
                # MultipleChoiceWidget needs a list of pks, not object instances.
                qs = f.value_from_object(instance)
                if qs._result_cache is not None:
                    data[verbose_name] = [item.pk for item in qs]
                else:
                    data[verbose_name] = list(qs.values_list('pk', flat=True))
        else:
            data[verbose_name] = f.value_from_object(instance)
    return data