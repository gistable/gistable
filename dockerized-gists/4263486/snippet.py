class FilterSetMixin(object):
    filter_class = None
 
    def get_filterset(self, queryset):
        if self.model is None and self.filter_class is None:
            raise TypeError("object_filter must be called with either model or filter_class")
        if self.model is None:
            self.model = self.filter_class._meta.model
        if self.filter_class is None:
            meta = type('Meta', (object,), {'model': self.model})
            self.filter_class = type('%sFilterSet' % self.model._meta.object_name, (django_filters.FilterSet,),
                {'Meta': meta})
        return self.filter_class(self.request.GET or None, queryset=queryset)
 
    def get_context_data(self, **kwargs):
        # share the same queryset between the filter and class based view
        filterset = self.get_filterset(kwargs['object_list'])
        kwargs['object_list'] = filterset.qs
        context = super(FilterSetMixin, self).get_context_data(**kwargs)
        context['filter'] = filterset
        return context