# -*- coding: utf-8 -*-
#TODO write a patch and submit to haystack


def patch():
    from django.db.models import Q

    from haystack import connections
    from haystack.backends import BaseEngine, log_query
    from haystack.models import SearchResult
    from haystack.backends import simple_backend

    class SimpleSearchBackendPatched(simple_backend.SimpleSearchBackend):
        @log_query
        def search(self, query_string, sort_by=None, start_offset=0,
                end_offset=None, fields='', highlight=False, facets=None,
                date_facets=None, query_facets=None, narrow_queries=None,
                spelling_query=None, within=None, dwithin=None,
                distance_point=None, models=None,
                limit_to_registered_models=None, result_class=None, **kwargs):
            hits = 0
            results = []

            if result_class is None:
                result_class = SearchResult

            if query_string:
                for model in connections[self.connection_alias].\
                                    get_unified_index().get_indexed_models():
                    if models and not model in models:
                        continue

                    if query_string == '*':
                        qs = model.objects.all()
                    else:
                        for term in query_string.split():
                            queries = []

                            for field in model._meta._fields():
                                if hasattr(field, 'related'):
                                    continue

                                if not field.get_internal_type() in \
                                    ('TextField', 'CharField', 'SlugField'):
                                    continue

                                queries.append(Q(**{'%s__icontains' %
                                    field.name: term}))

                        qs = model.objects.filter(reduce(lambda x, y: x | y,
                                                  queries))

                    hits += len(qs)

                    for match in qs:
                        result = result_class(match._meta.app_label,
                            match._meta.module_name, match.pk, 0,
                                **match.__dict__)
                        # For efficiency.
                        result._model = match.__class__
                        result._object = match
                        results.append(result)

            return {
                'results': results,
                'hits': hits,
            }

    simple_backend.SimpleSearchBackend = SimpleSearchBackendPatched

    class SimpleEnginePatched(BaseEngine):
        backend = simple_backend.SimpleSearchBackend
        query = simple_backend.SimpleSearchQuery

    simple_backend.SimpleEngine = SimpleEnginePatched