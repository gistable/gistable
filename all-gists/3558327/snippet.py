from django.contrib.admin import FieldListFilter
from django.utils.translation import ugettext as _


class ActiveValueFilter(FieldListFilter):
    """list_filter which displays only the values for a field which are in use

    This is handy when a large range has been filtered in some way which means
    most of the potential values aren't currently in use. This requires a 
    queryset field or annotation named "item_count" to be present so it can
    simply exclude anything where item_count=0.

    Usage::
    
    class MyAdmin(ModelAdmin):
        …
        list_filter = (('title', ActiveValueFilter))
    """

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '%s__exact' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        super(ActiveValueFilter, self).__init__(field, request, params,
                                                  model, model_admin,
                                                  field_path)

        qs = model_admin.queryset(request)

        qs = qs.exclude(item_count=0)

        qs = qs.order_by(field.name).values_list(field.name, flat=True)

        self.active_values = qs.distinct()

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
            'display': _('All')
        }

        for lookup in self.active_values:
            yield {
                'selected': lookup == self.lookup_val,
                'query_string': cl.get_query_string({
                                    self.lookup_kwarg: lookup}),
                'display': lookup,
            }
