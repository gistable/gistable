import django_filters


class CommaSeparatedValueFilter(django_filters.CharFilter):
    """Accept comma separated string as value and convert it to list.

    It's useful for __in lookups.
    """

    def filter(self, qs, value):
        if value:
            value = value.split(',')

        return super(CommaSeparatedValueFilter, self).filter(qs, value)