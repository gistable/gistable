# -*- coding: utf-8 -*-
from django.views.generic import ListView

class SortableListView(ListView):
    allowed_sort_fields = ()
    sort_default = None
    sort_key = 'sort'
    sort_field_splitter = '-'
    sort_ascending_postfix = 'up'
    sort_descending_postfix = 'down'
    sort_allow_post = False
    sort_field_map = {}


    def get_sort_key(self):
        return self.sort_key

    def get_allowed_sort_fields(self):
        return self.allowed_sort_fields

    def get_queryset(self):
        return self.sort_queryset(super(SortableListView, self).get_queryset())

    def sort_queryset(self, queryset):
        self.sorted_by = None
        self.sorted_direction = None
        if self.sort_default:
            queryset = queryset.order_by(self.sort_default)
        if self.sort_allow_post and self.request.method == 'POST':
            data = self.request.POST
        else:
            data = self.request.GET
        key = self.get_sort_key()
        if key not in data or self.sort_field_splitter not in data[key]:
            return queryset
        sort_field, direction = data[key].rsplit(self.sort_field_splitter, 1)
        if direction not in (self.sort_ascending_postfix, self.sort_descending_postfix):
            return queryset
        allowed_fields = self.get_allowed_sort_fields()
        if sort_field not in allowed_fields:
            return queryset
        self.sorted_by = sort_field
        self.sorted_direction = direction
        sort_field = self.sort_field_map.get(sort_field, sort_field)
        if direction == self.sort_descending_postfix:
            sort_field = '-' + sort_field
        return queryset.order_by(sort_field)

    def get_context_data(self, **kwargs):
        kwargs.update({'sorted_by': self.sorted_by, 'sorted_direction': self.sorted_direction})
        return super(SortableListView, self).get_context_data(**kwargs)
