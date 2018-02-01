#!/usr/bin/env python3.3

import netCDF4 as nc
import sys, argparse, inspect, json
import re
from pprint import pprint


# Check arguments

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--list', action='store_true')
# parser.add_argument('--vars', help='comma-separated variables')
args = parser.parse_args()


# Load and process data

data = nc.Dataset(args.input, 'r')
# pprint(inspect.getmembers(data))


if args.list:
	for key in data.variables:
		pprint((key, data.variables[key].dimensions))
	sys.exit()


result = {}
# for var in args.vars.split(','):
result['wind10m_u'] = list(map(lambda y: list(map(lambda x: "%.1f" % x, y)), list(data.variables['wind10m_u'])))
result['wind10m_v'] = list(map(lambda y: list(map(lambda x: "%.1f" % x, y)), list(data.variables['wind10m_v'])))
result['lat'] = list(map(lambda y: list(map(lambda x: "%.2f" % x, y)), list(data.variables['lat'])))
result['lon'] = list(map(lambda y: list(map(lambda x: "%.2f" % x, y)), list(data.variables['lon'])))
result['temp2m'] = list(map(lambda y: list(map(lambda x: "%.1f" % x, y)), list(data.variables['temp2m'])))
result['rain'] = list(map(lambda y: list(map(lambda x: "%.1f" % x, y)), list(data.variables['rain'])))
result['topo'] = list(map(lambda y: list(map(lambda x: "%.1f" % x, y)), list(data.variables['topo'])))
result['press'] = list(map(lambda y: list(map(lambda x: "%.1f" % x, y)), list(data.variables['press'][0])))



print(re.sub(r'"(-?\d+\.\d+)"', r'\1', json.dumps(result)));


data.close()