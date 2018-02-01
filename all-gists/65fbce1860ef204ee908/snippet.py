from collections import OrderedDict

from graphql.core.execution.executor import Executor
from graphql.core.execution.middlewares.gevent import GeventExecutionMiddleware, run_in_greenlet

import graphene


class Patron(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    age = graphene.ID()


class Query(graphene.ObjectType):

    patron = graphene.Field(Patron)

    @run_in_greenlet
    def resolve_patron(self, args, info):
        return Patron(id=1, name='Demo')

gevent_executor = Executor([GeventExecutionMiddleware()], map_type=OrderedDict)

schema = graphene.Schema(query=Query, executor=gevent_executor)
query = '''
    query something{
      patron {
        id
        name
      }
    }
'''
result = schema.execute(query)
print(result.data['patron'])
