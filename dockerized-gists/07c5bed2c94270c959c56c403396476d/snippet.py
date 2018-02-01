# set variable AWS_PROFILE= to credentials
import boto3
# CHANGE REGION HERE-
ec2 = boto3.resource('ec2', 'sa-east-1')
#check your own tags before run this script

#loop for tag Name
def tag_name():
    print "Loop for TAG Name"
    for volume in ec2.volumes.all():
      print(volume.id)
      for attachment in volume.attachments:
        print(attachment['InstanceId'])
        for name in ec2.Instance(attachment['InstanceId']).tags:
            if name['Key'] == 'Name':
              tag = volume.create_tags(
                DryRun=False,
                Resources=[volume.id],
                Tags=[{'Key':'Name','Value':name['Value']}]
              )

#loop for tag customerid

def tag_customerid():
    print "Loop for TAG CustomerID"
    for volume in ec2.volumes.all():
      print(volume.id)
      for attachment in volume.attachments:
        print(attachment['InstanceId'])
        for name in ec2.Instance(attachment['InstanceId']).tags:
            if name['Key'] == 'CustomerID':
              tag = volume.create_tags(
                DryRun=False,
                Resources=[volume.id],
                Tags=[{'Key':'CustomerID','Value':name['Value']}]
                )

#loop for tag project

def tag_project():
    print "Loop for TAG Project"
    for volume in ec2.volumes.all():
      print(volume.id)
      for attachment in volume.attachments:
        print(attachment['InstanceId'])
        for name in ec2.Instance(attachment['InstanceId']).tags:
            if name['Key'] == 'Project':
              tag = volume.create_tags(
                DryRun=False,
                Resources=[volume.id],
                Tags=[{'Key':'Project','Value':name['Value']}]
                )
#loop for tag envtype

def tag_envtype():
    print "Loop for TAG EnvType"
    for volume in ec2.volumes.all():
      print(volume.id)
      for attachment in volume.attachments:
        print(attachment['InstanceId'])
        for name in ec2.Instance(attachment['InstanceId']).tags:
            if name['Key'] == 'EnvType':
              tag = volume.create_tags(
                DryRun=False,
                Resources=[volume.id],
                Tags=[{'Key':'EnvType','Value':name['Value']}]
                )



tag_name()
tag_customerid()
tag_project()
tag_envtype()


#HERE a shell script to delete all tags from all volumes
#delete all EBS tags
#for i in `aws ec2 describe-volumes --profile <PROFILE_NAME> --output text | grep "vol-" | grep ATTACHMENTS | awk '{print $7}'`
#do
#	aws ec2 delete-tags --resources $i --profile <PROFILE_NAME>
#	echo $i
#done
