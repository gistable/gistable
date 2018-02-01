#!/usr/bin/env python
import boto3

client = boto3.client('s3')
Bucket = 'a-bucket'
Prefix = 'a-prefix' # leave blank to delete the entire contents
IsTruncated = True
MaxKeys = 1000
KeyMarker = None

while IsTruncated == True:
        if not KeyMarker:
                version_list = client.list_object_versions(
                        Bucket=Bucket,
                        MaxKeys=MaxKeys,
                        Prefix=Prefix)
        else:
                version_list = client.list_object_versions(
                        Bucket=Bucket,
                        MaxKeys=MaxKeys,
                        Prefix=Prefix,
                        KeyMarker=KeyMarker)

	try:
        	objects = []
        	versions = version_list['Versions']
        	for v in versions:
                	objects.append({'VersionId':v['VersionId'],'Key': v['Key']})
        	response = client.delete_objects(Bucket=Bucket,Delete={'Objects':objects})
		print response
	except:
		pass

        try:
		objects = []
        	delete_markers = version_list['DeleteMarkers']
        	for d in delete_markers:
                	objects.append({'VersionId':d['VersionId'],'Key': d['Key']})
        	response = client.delete_objects(Bucket=Bucket,Delete={'Objects':objects})
		print response
	except:
		pass

        IsTruncated = version_list['IsTruncated']
        KeyMarker = version_list['NextKeyMarker']