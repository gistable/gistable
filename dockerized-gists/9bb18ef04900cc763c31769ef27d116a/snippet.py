import boto3
import json
import datetime
import time
ec2 = boto3.resource('ec2', region_name='ap-southeast-2')

filters = [{
	'Name': 'tag:snapshot',
	'Values': [ 'yes' ]
}]
debugMode = False
mydate = str((datetime.datetime.today() + datetime.timedelta(1)).strftime("%Y%m%d"))
cleanDate = datetime.datetime.now()-datetime.timedelta(days=7)

def lambda_handler(event, context):
	base = ec2.instances.filter(Filters=filters)

	# Find the instance
	for instance in base:
		instanceid = instance.id
		print("[LOG] Found instance id: " + str(instanceid))

		# Find volumes attached to the instance
		for vol in instance.volumes.all():
			print("[LOG] Found volume id: " + str(vol.id))
			desc = str("Volume snapshot : " + str(vol.id) + " " + mydate + "-automated")

			# Create snapshot
			if debugMode == True:
				print("[DEBUG]: Description : " + str (desc))
				print("[DEBUG]: tags - ")
				print(tag_cleanup(instance,vol.id))
			else:
				snapshot = ec2.create_snapshot(VolumeId=vol.id, Description=desc)
				tag = snapshot.create_tags(Tags=(tag_cleanup(instance,vol.id)))
				snapshot.create_tags(Tags=(tag_snapshot('volume',vol.id)))
				snapshot.create_tags(Tags=(tag_snapshot('instance',instanceid)))
				print("[LOG] Snapshot id : " + str(snapshot.id))

	#clean up old snapshots
	for snap in ec2.snapshots.all():
		#verify results have a value
		if snap.description.endswith("-automated"):
			#Pull the snapshot date
			snapDate = snap.start_time.replace(tzinfo=None)
			print("[LOG] " + str(snapDate) + " vs " + str(cleanDate))
			#Compare the clean dates
			if cleanDate > snapDate:
				print("[LOG] Snapshot id found :" + snap.id)
				print("[LOG] Dates : " + str(snapDate) + " vs " + str(cleanDate))
				print("[LOG] Deleting: " + snap.id + " - From: " + str(snapDate))
				if debugMode != True:
					try:
						snapshot = snap.delete(snap.id)
						print("Deleted snapshot " + snap.id)
					except:
						#if we timeout because of a rate limit being exceeded, give it a rest of a few seconds
						print("[INFO]: Waiting 5 Seconds for the API to Chill")
						time.sleep(5)
						snapshot = snap.delete(snap.id)
						print("[INFO] " + str(snapshot))

def tag_cleanup(instance, detail):
	tempTags=[]
	v={}

	for t in instance.tags:
	#pull the name tag
		if t['Key'] == 'Name':
			v['Value'] = t['Value'] + "_" + str(detail) + "_" + str(mydate)
			v['Key'] = 'Name'
			tempTags.append(v)
		elif t['Key'] == 'app':
			v['Value'] = t['Value']
			v['Key'] = 'app'
			tempTags.append(t)

	return(tempTags)

def tag_snapshot(key, value):
	tempTags=[]
	v={}
	v['Value'] = str(value)
	v['Key'] = str(key)
	tempTags.append(v)
	return(tempTags)