#!/usr/bin/python
'''
reposado update notification: reports changed Apple products between repo_sync runs

Checks the current list of updates versus the previous list of updates and
reports on the changes. Run this script after your repo_sync run to see the
changes between syncs. You can then hand this report off in email if you wish.

For example:

  repo_sync
  reponotify.py | mail -Es 'Reposado updates' reposado@example.com

Note that this script requires write permission in the UpdatesRootDir
directory of your reposado. This is so that it can write the tracking file
that is used between runs to compute the difference in update lists.

Note also it needs access to the "reposadocommon" Python library. This means
you probably want to place it in the "code" directory of your reposado
installation.
'''

from reposadolib import reposadocommon
from sys import exit
import os
import pickle

root_dir = reposadocommon.pref('UpdatesRootDir')
state_file = os.path.join(root_dir, 'reponotify.pickle')

products = reposadocommon.getProductInfo()

cur_apple_prods = []

for prod_id in products.keys():
	if len(products[prod_id]['AppleCatalogs']) > 0:
		cur_apple_prods.append(prod_id)

try:
	with open(state_file, 'rb') as pF:
		prev_apple_prods = pickle.load(pF)
except:
	# if there's a problem reading the file then assume we're "up to date" by
	# assigning all the current updates to the previous updates (no deltas)
	prev_apple_prods = cur_apple_prods

cur_set = set(cur_apple_prods)
prev_set = set(prev_apple_prods)

new_prods = cur_set.difference(prev_set)
del_prods = prev_set.difference(cur_set)

if new_prods:
	config_data_prods = reposadocommon.check_or_remove_config_data_attribute(new_prods, products=products)
	print 'New Products Added to Apple Catalog'
	print
	for prod_id in new_prods:
		print prod_id,
		if prod_id in config_data_prods:
			print '(Config)',
		print products[prod_id]['title'].encode('utf-8'),
		print products[prod_id]['version'],
		print products[prod_id]['PostDate']
	print

if del_prods:
	print 'Deprecated Products Removed from Apple Catalog (but possibly still in repo)'
	print
	for prod_id in del_prods:
		print prod_id,
		if prod_id in products.keys():
			print products[prod_id]['title'].encode('utf-8'),
			print products[prod_id]['version'],
			print products[prod_id]['PostDate']
	print

with open(state_file, 'wb') as pF:
	pickle.dump(cur_apple_prods, pF)
