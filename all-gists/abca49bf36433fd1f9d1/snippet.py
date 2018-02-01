import json
import chef

# Copy your .chef directory into the root folder of the deployment package:
# http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html#deployment-pkg-for-virtualenv
# See also https://github.com/coderanger/pychef/issues/41

print('Loading function')

def lambda_handler(event, context):
  print("Event received: " + json.dumps(event))
  for record in event['Records']:
    if 'Sns' in record:
      message = json.loads(record['Sns']['Message'])
      if message['Event'] == 'autoscaling:EC2_INSTANCE_TERMINATE':
        instance_id = message['EC2InstanceId']
        print("instance_id = " + instance_id)

        try:
          chef_api = chef.autoconfigure()
        except:
          raise Exception('Could not configure Chef!')

        try:
          rows = chef.Search('node', 'ec2_instance_id:' + instance_id)
        except:
          raise Exception('Could not search for nodes with ec2_instance_id: ' + instance_id)

        for row in rows:
          try:
            n = chef.Node(row['name'])
          except:
            raise Exception('Could not fetch node object for ' + row['name'])

          print("node:   " + str(n))

          try:
            c = chef.Client(row['name'])
          except:
            raise Exception('Could not fetch client object for ' + row['name'])

          print("client: " + str(c))

          try:
            n.delete()
          except:
            raise Exception('Could not delete node ' + str(n))

          try:
            c.delete()
          except:
            raise Exception('Could not delete client ' + str(n))

      else:
        raise Exception('Could not process SNS message')
