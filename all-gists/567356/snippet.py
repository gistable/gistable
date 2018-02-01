def attach_foreignkey(objects, field, select_related=None):
    """
    Shortcut method which handles a pythonic LEFT OUTER JOIN.
    
    ``attach_foreignkey(posts, Post.thread)``
    """
    field = field.field
    qs = field.rel.to.objects.filter(pk__in=distinct(getattr(o, field.column) for o in objects))
    if select_related:
        qs = qs.select_related(*select_related)
    queryset = queryset_to_dict(qs)
    for o in objects:
        setattr(o, '_%s_cache' % (field.name), queryset.get(getattr(o, field.column)))