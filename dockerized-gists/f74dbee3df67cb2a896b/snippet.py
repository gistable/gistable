import boto
import datetime

cw = boto.connect_cloudwatch()

instance_id = boto.utils.get_instance_metadata()['instance-id']

now = datetime.datetime.utcnow()
start_time = now - datetime.timedelta(days=1)
namespace = "System"
metric_name = "load_avg"

cw.get_metric_statistics(period=60,
	start_time=start_time,
	end_time=now,
	metric_name=metric_name,
	namespace=namespace,
	statistics=['Maximum'],
	dimensions={'InstanceId': [instance_id]})