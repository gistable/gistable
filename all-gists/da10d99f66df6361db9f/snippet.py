import boto.utils
import boto.beanstalk

good_statuses = ('Launching', 'Updating', 'Ready')
def get_eb_environment_description():
    identity_document = boto.utils.get_instance_identity()['document']

    connection = boto.beanstalk.connect_to_region(identity_document['region'])

    envs = (e for e in  
        connection.describe_environments()
        ['DescribeEnvironmentsResponse']
        ['DescribeEnvironmentsResult']
        ['Environments']
    )   

    for env in envs:
        if env['Status'] not in good_statuses:
            continue
        resources = ( 
            connection.describe_environment_resources(
                environment_name=env['EnvironmentName']
            )   
            ['DescribeEnvironmentResourcesResponse']
            ['DescribeEnvironmentResourcesResult']
            ['EnvironmentResources']
        )   

        for instance in resources['Instances']:
            if instance['Id'] == identity_document['instanceId']:
                return env 

    return None
