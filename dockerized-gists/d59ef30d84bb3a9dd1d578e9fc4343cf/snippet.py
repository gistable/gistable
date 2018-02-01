import graphene
import boto3


class Cluster(graphene.ObjectType):
    arn = graphene.String(description='Cluster ARN')
    name = graphene.String(description='Cluster Name')
    status = graphene.String(description='Cluster Status')
    registeredContainerInstancesCount = graphene.Int(description='Container Instances Count')
    runningTasksCount = graphene.Int(description='Running Tasks Count')
    pendingTasksCount = graphene.Int(description='Pending Tasks Count')
    activeServicesCount = graphene.Int(description='Active Services Count')


class Query(graphene.ObjectType):

    clusters = graphene.List(Cluster)

    def resolve_clusters(self, args, context, info):
        client = boto3.client('ecs')
        response = client.list_clusters()
        response = client.describe_clusters(clusters=response['clusterArns'])
        clusters = []
        for cluster in response['clusters']:
            '''
            {
            'clusterArn': 'string',
            'clusterName': 'string',
            'status': 'string',
            'registeredContainerInstancesCount': 123,
            'runningTasksCount': 123,
            'pendingTasksCount': 123,
            'activeServicesCount': 123
            }
            '''
            obj = Cluster(arn=cluster['clusterArn'],
                          name=cluster['clusterName'],
                          status=cluster['status'],
                          registeredContainerInstancesCount=cluster['registeredContainerInstancesCount'],
                          runningTasksCount=cluster['runningTasksCount'],
                          pendingTasksCount=cluster['pendingTasksCount'],
                          activeServicesCount=cluster['activeServicesCount'])
            clusters.append(obj)
        return clusters

schema = graphene.Schema(query=Query)
query = '''
    query something{
      clusters {
        arn
        name
        status
        activeServicesCount
      }
    }
'''


if __name__ == '__main__':
    result = schema.execute(query)
    print(result.data)