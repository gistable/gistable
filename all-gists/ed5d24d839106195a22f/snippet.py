#!/usr/bin/python
 
import json
import datetime
 
try:
    from boto import ec2
except ImportError:
    print '[!] Install boto: pip install boto'
    sys.exit(1)
try:
    from influxdb.influxdb08 import  InfluxDBClient
except ImportError:
    print '[!] Install InfluxDBClient: pip install InfluxDBClient'
    sys.exit(1)
try:
    import MySQLdb as mdb
except ImportError:
    print '[!] Install MySQLdb: pip install MySQLdb'
    sys.exit(1)
 
EC2_STATUS = {
    "Time": "time",
    "InstanceId": "name",
    "InstanceType": "name",
    "PrivateIpAddress": "name",
    "LaunchTime": "name",
    "PartialUpfront":"gauge",
    "SecurityGroup": "name",
    "Price":"gauge",
    "Status":"name",
    }
 
def get_aws_prices(instance_type):
    con = mdb.connect('localhost', 'root', '', 'test')
    try:
        ret=""
        cur = con.cursor()
        #cur.execute("select price from awsprices2 where type='"+instance_type+"' and region = 'eu-west-1' and payment_type= 'noUpfront' and os  = 'linux' limit 1")
        cur.execute("select price from awsprices2 where type='"+instance_type+"'and region = 'eu-west-1' and reserved_od='ondemand' and os  = 'linux' limit 1")
        result = cur.fetchall()
        for row in result:
            ret = row[0]
            continue
 
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:
        if con:
            con.close()
        return ret
 
 
 
def ec2_conn():
    conn = ec2.connect_to_region('eu-west-1')
    reservations = conn.get_all_instances()
    instances = [i for r in reservations for i in r.instances]
    stats  = dict.fromkeys(EC2_STATUS.keys(), 0)
    time = str(datetime.datetime.now())
 
    for instance in instances:
        try :
            if instance.private_ip_address is None:
                stats["PrivateIpAddress"] = "0" 
            else:
                stats["PrivateIpAddress"]= instance.private_ip_address
        except :
            stats["PrivateIpAddress"] = "0"              
            continue
        stats["Time"] = time
        stats["InstanceId"]= instance.id
        stats["InstanceType"]= instance.instance_type            
        stats["LaunchTime"]= instance.launch_time
        stats["Price"]=get_aws_prices(instance.instance_type)
        stats["Status"]=instance.state
        # for sg in instance.security_groups:
        stats["SecurityGroup"]=""
        set_curl (stats)
        #print  (stats)
 
def set_curl(stats):
    print 'curl -X POST -d \'[{"name":"ec2_desc","columns":["InstanceId", "InstanceType","PrivateIpAddress", "Time" , "Price","SecurityGroup", "Status"], "points":[["'+stats["InstanceId"]+'","'+stats["InstanceType"]+'","'+ stats["PrivateIpAddress"]+'","'+stats["Time"]+'", '+stats["Price"]+', "'+stats["SecurityGroup"]+'" , "'+stats["Status"]+'"  ]]}]'+"\', "+ '\'http://xx.xx.xx.xx:8086/db/mydb/series?u=root&p=root\';'
 
def filter_data(obj):
        if type(obj) in (int, float, str, bool):
                return obj
        elif type(obj) == unicode:
                return str(obj)
        elif type(obj) in (list, tuple, set):
                obj = list(obj)
                for i,v in enumerate(obj):
                        obj[i] = filter_data(v)
        elif type(obj) == dict:
                for i,v in obj.iteritems():
                        obj[i] = filter_data(v)
        else:
                print "invalid object in data, converting to string"
                obj = str(obj) 
        return obj
 
if __name__ == '__main__':
    #args = parser.parse_args()
    ec2_conn()
    #output(request_result, args.graphite, args.graphite_id)