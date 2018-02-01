from itertools import chain
from operator import attrgetter


# ascending oreder
result_list = sorted(
    chain(queryset1, queryset2),
    key=attrgetter('date_created'))
    
# descending order
result_list = sorted(
    chain(queryset1, queryset2),
    key=attrgetter('date_created'),
    reverse=True)