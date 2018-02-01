import boto3
import logging
import datetime
import re
import time

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

#define the connection
ec2 = boto3.resource('ec2', region_name="us-west-2")

#set the snapshot removal offset
cleanDate = datetime.datetime.now()-datetime.timedelta(days=5)

#Set this to True if you don't want the function to perform any actions
debugMode = False

def lambda_handler(event, context):
    
    if debugMode == True:
        print("-------DEBUG MODE----------")
 
    #snapshop the instances
    for vol in ec2.volumes.all():
        tempTags=[]
        
        #Prepare Volume tags to be importated into the snapshot
        if vol.tags != None:
            for t in vol.tags:
                
                #pull the name tag
                if t['Key'] == 'Name':
                    instanceName =  t['Value']
                    tempTags.append(t)
                else:
                    tempTags.append(t)
        else:
            print("Issue retriving tag")
            instanceName = "NoName"
            t['Key'] = 'Name'
            t['Value'] = 'Missing'
            tempTags.append(t)
        
        description = str(datetime.datetime.now()) + "-" + instanceName + "-" + vol.id + "-automated"
        
        if debugMode != True:
            #snapshot that server
            snapshot = ec2.create_snapshot(VolumeId=vol.id, Description=description)
            
            #write the tags to the snapshot
            tags = snapshot.create_tags(
                    Tags=tempTags
                )
            print("[LOG] " + str(snapshot))
            
        else:
            print("[DEBUG] " + str(tempTags))
    
    print "[LOG] Cleaning out old entries starting on " + str(cleanDate)
    
    #clean up old snapshots
    for snap in ec2.snapshots.all():

        #veryify results have a value
        if snap.description.endswith("-automated"): 
            
            #Pull the snapshot date
            snapDate = snap.start_time.replace(tzinfo=None)
            if debugMode == True:
                print("[DEBUG] " + str(snapDate) +" vs " + str(cleanDate)) 
            
            #Compare the clean dates
            if cleanDate > snapDate:
                print("[INFO] Deleteing: " + snap.id + " - From: " + str(snapDate))
                if debugMode != True:
                    try:
                        snapshot = snap.delete()
                    except:
                        
                        #if we timeout because of a rate limit being exceeded, give it a rest of a few seconds
                        print("[INFO]: Waiting 5 Seconds for the API to Chill")
                        time.sleep(5)
                        snapshot = snap.delete()
                    print("[INFO] " + str(snapshot))