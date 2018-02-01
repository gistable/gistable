def paginate(ctx_name):
    """
    View decorator that handles pagination of a ListObject. Expects to find it
    in the TemplateResponse context under the name ``ctx_name``.

    This needs to not force delivery of the ListObject.

    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            ctx = response.context_data
            pagesize, pagenum = pagination.from_request(request)
            ctx[ctx_name] = ctx[ctx_name].paginate(pagesize, pagenum)
            # the lambda here makes Pager fetch the total result count
            # lazily; another decorator might modify the result set yet.
            ctx["pager"] = pagination.Pager(
                lambda: ctx[ctx_name].totalResults, pagesize, pagenum)
            return response

        return _wrapped_view

    return decorator