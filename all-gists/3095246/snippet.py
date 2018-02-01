'''
Cache the generic relation field of all the objects 
in the queryset, using larger bulk queries ahead of time.

Improved from original by Daniel Roseman:
http://blog.roseman.org.uk/2010/02/22/django-patterns-part-4-forwards-generic-relations/
'''


def cache_generics(queryset):
    generics = {}
    for item in queryset:
        if item.object_id is not None:
            generics.setdefault(item.content_type_id, set()).add(item.object_id)

    content_types = ContentType.objects.in_bulk(generics.keys())

    relations = {}
    for ct, fk_list in generics.iteritems():
        ct_model = content_types[ct].model_class()
        relations[ct] = ct_model.objects.in_bulk(list(fk_list))

    for item in queryset:
        try:
            cached_val = relations[item.content_type_id][item.object_id]
        except KeyError:
            cached_val = None
        setattr(item, '_content_object_cache', cached_val)  