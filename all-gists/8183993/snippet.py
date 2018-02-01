from django.core.paginator import Paginator, InvalidPage, EmptyPage


def paginate(request, object_list, limit=10, page_range=10, object_pk=None):
    paginator = Paginator(object_list, limit)
    page = None
    if object_pk:
        if hasattr(object_list, 'values_list') and callable(
                object_list.values_list):
            object_list = list(object_list.values_list('pk', flat=True))
        else:
            try:
                object_list = [o.pk for o in object_list]
            except (AttributeError, TypeError):
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list).
                pass
        try:
            object_index = object_list.index(object_pk)
        except ValueError:
            pass
        else:
            page = int(ceil(float(object_index + 1) / limit))
    try:
        page = page or int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        page_query = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page_query = paginator.page(paginator.num_pages)

    if page_query.paginator.num_pages <= page_range:
        range_start = 1
        range_end = page_query.paginator.num_pages + 1
    else:
        range_start = page - int(page_range / 2)
        if range_start < 1:
            range_start = 1
        range_end = range_start + page_range
        if range_end >= page_query.paginator.num_pages:
            range_start = page_query.paginator.num_pages - page_range + 1
            range_end = page_query.paginator.num_pages + 1
    page_query.neighbor_range = range(range_start, range_end)

    return page_query
