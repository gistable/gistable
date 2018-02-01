from graphql.execution.executors.sync import SyncExecutor

"""
Usage example:

    from functools import partial

    class MyServiceCache(BulkRequestCache):
        def __init__():
            self.requested_values = set()
            self.results = {}

        def request_value(self, id):
            self.requested_values.add(id)

        def retrieve_value(self, id):
            if id not in self.results:
                self.request_value(id)
                self.results = retrieve_expensive_values(self.requested_values)  # <-- Bulk request/process things here
            return self.results.get(id)

    def get_value_from_service(id):
        MyServiceCache.get().request_value(id)
        retrieve_value_fn = partial(MyServiceCache.get().retrieve_value, id)
        return LazyPromise(retrieve_value_fn)

    class Query(ObjectType):
        expensive = graphene.String()
        expensive_two = graphene.String()

        @graphene.resolve_only_args
        def resolve_expensive(self):
            return get_value_from_service(1)

        @graphene.resolve_only_args
        def resolve_expensive_two(self):
            return get_value_from_service(2)


    schema = graphene.Schema(query=Query)
    view = GraphQLView.as_view(schema=schema, executor=LazySyncExecutor(), middleware=[LazyExecutionMiddleware])

"""

_graphql_pre_finish = []
_graphql_pre_execute = []


class LazyExecutionMiddleware(object):
    def resolve(self, next, root, args, context, info):
        if root is None:
            _graphql_pre_finish.clear()

            while _graphql_pre_execute:
                cb = _graphql_pre_execute.pop(0)
                cb()
        return next(root, args, context, info)


class LazySyncExecutor(SyncExecutor):
    def wait_until_finished(self):
        for cb in _graphql_pre_finish:
            cb()


class LazyPromise:
    def __init__(self, resolve_fn):
        # resolve_fn is used to execute+retrieve the actual promise value
        assert callable(resolve_fn), "Expected resolve_fn to be callable, received %s instead" % type(resolve_fn)
        self.resolve_fn = resolve_fn

        # Result of resolve_fn, once executed.
        self.is_resolved = False
        self.result = None
        self.error = None

        # Register do_resolve function in global list of lazy functions.
        _graphql_pre_finish.append(self.do_resolve)

        # List of callbacks registered via `then`. To be called after resolve_fn
        self.success_callbacks = []
        self.failure_callbacks = []

    def then(self, success, failure):
        if self.is_resolved:
            if self.error:
                failure(self.error)
            else:
                success(self.result)
        else:
            self.success_callbacks.append(success)
            self.failure_callbacks.append(failure)

    def do_resolve(self):
        try:
            self.result = self.resolve_fn()
            [cb(self.result) for cb in self.success_callbacks]
        except Exception as e:
            self.error = e
            [cb(self.error) for cb in self.failure_callbacks]
        self.is_resolved = True


class BulkRequestCache:
    instance = None

    @classmethod
    def _reset(cls):
        cls.instance = None

    @classmethod
    def get(cls, *args, **kwargs):
        # When we create the first instance, register the clear function in global list of pre_execute functions.
        if cls.instance is None:
            _graphql_pre_execute.append(cls._reset)
            cls.instance = cls(*args, **kwargs)
        return cls.instance

    def request_value(self, *args, **kwargs):
        # Called to register the need for some data.
        raise NotImplementedError

    def retrieve_value(self, *args, **kwargs):
        # Called to retrieve some data. If it's not available yet, it should be fetched now and the function should
        # block until it's either available or a failure has occurred.
        raise NotImplementedError


class MultiBulkRequestCache(BulkRequestCache):
    instances = {}

    @classmethod
    def get(cls, identifier, *args, **kwargs):
        # When we create the first instance, register the clear function in global list of pre_execute functions.
        if not cls.instances:
            _graphql_pre_execute.append(cls.instances.clear)

        # Get a cache for the given identifier. Every identifier has exactly one cache instance.
        if identifier not in cls.instances:
            cls.instances[identifier] = cls(identifier, *args, **kwargs)
        return cls.instances[identifier]
