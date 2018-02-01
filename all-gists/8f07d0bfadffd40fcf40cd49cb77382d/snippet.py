import cfscrape
import json
import sys
import argparse
import requests
import logging
import time
import random

from pgoapi import PGoApi
from pgoapi.exceptions import ServerSideRequestThrottlingException

from queue import Queue
from threading import Thread


# Ignore countries
ignore = [ 'China' ]

##### END OF CONFIGURATION #####
logging.basicConfig(format='%(asctime)s %(message)s')
log = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--proxy-file", help="Text file containing proxies. One proxy per line like http://x.x.x.x:3128")
parser.add_argument("-o", "--output-file", help="Output file with working proxies", default="working_proxies.txt")
parser.add_argument("--proxychains", help="Output in proxychains-ng format. Something like 'http x.x.x.x 3128'", action='store_true')
parser.add_argument("-t", "--timeout", help="Proxy timeout. Default is 15 seconds.", default=15, type=float)
parser.add_argument("-v", "--verbose", help="Run in the verbose mode.", action='store_true')
parser.add_argument("-u", "--username", help="Username if you want to test account connectivity")
parser.add_argument("-p", "--password", help="Password if you want to test account connectivity")
args = parser.parse_args()

working_proxies = []

def check_pogo_login(proxy, username, password):
	try:
		api = PGoApi()
		api.set_proxy({'http': proxy, 'https': proxy})
		api.set_position(40.7127837, -74.005941, 0.0)
		api.login('ptc', username, password)
		time.sleep(1)
		req = api.create_request()
		req.get_inventory()
		response = req.call()
		if response['status_code'] == 3:
			log.error("The account you're using to test is banned. Try another one.")
			sys.exit(1)
	except ServerSideRequestThrottlingException as e:
		secs = random.randrange(700,1100) / 100;
		log.debug("[ %s\t] Server side throttling, Waiting %s seconds!",proxy, secs);
		time.sleep(secs)
		check_pogo_login(proxy, username, password)


def check_single_proxy(proxy_queue, timeout, working_proxies):

	proxy_test_url = 'https://sso.pokemon.com/'
	proxy = proxy_queue.get_nowait()

	if proxy:
		try:
			proxy_response = requests.get(proxy_test_url, proxies={'http': proxy, 'https': proxy}, timeout=timeout)

			if proxy_response.status_code == 200:
				# Test logging in
				if args.username and args.password:
					check_pogo_login(proxy, args.username, args.password)

				log.info("[ %s\t] Ready for PokemonGo!",proxy)
				proxy_queue.task_done()
				working_proxies.append(proxy)
				return True
			else:
				proxy_error = "Invalid Status Code - " + str(proxy_response.status_code)

		except requests.ConnectTimeout:
			proxy_error = "Proxy timeout after " + str(timeout) + " seconds."

		except requests.ConnectionError:
			proxy_error = "Fail to connect to the proxy."
		except Exception as e:
			proxy_error = e
	else:
			proxy_error = "Empty Proxy."

	log.info("[ %s\t] Error: %s",proxy,proxy_error)
	proxy_queue.task_done()
	return False

def save_to_file( proxies, file ):

	file = open( file, "w" )
	for proxy in proxies:
		if args.proxychains:
			# Split the protocol
			protocol, address = proxy.split("://",2)
			# address = proxy.split("://")[1]
			# Split the port
			ip, port = address.split(":",2)
			# Write to file
			file.write( protocol + " " + ip + " " + port + "\n")
		else:
			file.write(proxy + "\n")

if __name__ == "__main__":
	log.setLevel(logging.INFO);

	if args.verbose:
		log.setLevel(logging.DEBUG);
		log.debug("Running in verbose mode (-v).")

	if args.username and args.password:
		log.info("Running with account testing. Going try to login into %s on each step.", args.username)

	if args.proxy_file:
		with open(args.proxy_file) as f:
			proxies = f.read().splitlines()
	else:
		# Download the URL
		url = "http://coolproxies.com/pl/proxylist.php?grid_id=list1&_search=true&nd=1471879089948&rows=1000&jqgrid_page=1&sidx=ping&sord=asc&filters=%7B%22groupOp%22%3A%22AND%22%2C%22rules%22%3A%5B%7B%22field%22%3A%22type_name%22%2C%22op%22%3A%22cn%22%2C%22data%22%3A%22HTTP%22%7D%2C%7B%22field%22%3A%22support_ssl%22%2C%22op%22%3A%22cn%22%2C%22data%22%3A%221%22%7D%5D%7D"
		scraper = cfscrape.create_scraper()
		response = scraper.get(url)
		data = json.loads(response.content)
		log.info("Downloaded %s proxies from %s", len(data['rows']), url)
		proxies = []
		for proxy in data['rows']:
			if proxy['countryname'] in ignore:
				continue;
			if proxy['ping'] == "0":
				continue;
			proxies.append("http://" + proxy['proxy'])

	log.info( "Read %s proxies. Starting proxies availability test...", len(proxies) )

	# Initialize the Proxy Queue
	proxy_queue = Queue()
	for proxy in proxies:
		proxy_queue.put(proxy)

	for i in range(0, len(proxies)):
		if args.username and args.password:
			time.sleep(1)
		log.debug("Launching thread %s", i)
		t = Thread(target=check_single_proxy,
				   name='check_proxy',
				   args=(proxy_queue, args.timeout, working_proxies))
		t.daemon = True
		t.start()

	# Wait for the queue to finish
	proxy_queue.join()

	log.info( "Found %s working proxies! Writing to %s", len(working_proxies), args.output_file )
	save_to_file( working_proxies, args.output_file )
	sys.exit(0)
