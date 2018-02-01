"""
Auto Discover proof of concept for Cabot
To use copy to cabot\cabotapp\management\commands\AutoDiscover.py
Run with this command: sh -ac ' . ./conf/production.env; python manage.py AutoDiscover'
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from cabot.cabotapp.models import *
from cabot.cabotapp.graphite import *


def AddServiceCheck(service, name, metric, check_type, value, debounce=0):
	"""
	Create check for metric, and add to service
	"""
	check, bCreated = GraphiteStatusCheck.objects.get_or_create(
									name = name,
									metric = metric,
									defaults = {
										"check_type": check_type,
										"value": value,
										"created_by_id": 1,  # hard coded to user 1
										"importance": Service.ERROR_STATUS,
										}
									)

	service.status_checks.add(check);

class Command(BaseCommand):
	def handle(self, *args, **options):

		user = User.objects.get(username="root");

		# search for all servers
		metrics = get_matching_metrics("servers.*"); 
		for metric in metrics["metrics"]:
			print metric["path"], metric["name"]
			server = metric["name"]
			server_path = metric["path"];

			# get or create server
			service, created = Service.objects.get_or_create(name=server, defaults={"email_alert": True, "hipchat_alert": False})
			service.users_to_notify.add(user)

			# find all disks and add a check for percent free less then 5%
			disk_metrics = get_matching_metrics("%sdiskspace.*" % (server_path)); # servers.www01.diskspace.root.gigabyte_percentfree			
			for disk_metric in disk_metrics["metrics"]:
				AddServiceCheck(service, 
									"%s %s free" % (server, disk_metric["name"]), 
									"%sgigabyte_percentfree" % (disk_metric["path"]), 
									"<", 
									"5.0");

			# Add check for load over 5
			AddServiceCheck(service, 
								"%s load" % (server, ), 
								"%sloadavg.05" % (server_path, ), 
								">", 
								"5.0");

			# Add check for low swap+free  memory
			AddServiceCheck(service, 
								"%s low mem" % (server, ), 
								"sumSeries(%smemory.SwapFree, %smemory.MemFree)"% (server_path, server_path), 
								"<", 
								"1000000");