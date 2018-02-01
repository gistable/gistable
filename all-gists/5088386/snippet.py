from django.db import models
import django_filters
import operator


class SearchFilter(django_filters.CharFilter):
    
    def __init__(self, name='pk', search_fields=[], *args, **kwargs):
        super(SearchFilter, self).__init__(name, *args, **kwargs)
        self.search_fields = search_fields
    
    def filter(self, qs, keywords):
        
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name
        
        if self.search_fields and keywords:
            orm_lookups = map(construct_search, self.search_fields)
            for keyword in keywords.split():
                or_queries = [models.Q(**{orm_lookup: keyword})
                              for orm_lookup in orm_lookups]
                qs = qs.filter(reduce(operator.or_, or_queries))

        return qs


class ReportFilter(django_filters.FilterSet):

    query = SearchFilter(search_fields=[
        'tag_number', 'contact_name', 'contact_email', 'state', 'species__name'])
    state = StateValueFilter(name='state', widget=FilterLinkWidget)

    class Meta:
        model = Report
        fields = ['query', 'state', 'species']
