from __future__ import division
import urllib, json, string, datetime
from itertools import permutations
from math import log

def _bf(V, E, src):

	# init
	dist = dict(zip(V, [float('Inf') for v in V]))
	pred = dict(zip(V, [None for v in V]))
	dist[src] = 0

	# relax
	valid_pairs = [(u,v) for (u,v) in permutations(V, 2) if E[u].has_key(v)]
	for i in range(len(V)-1):
		for (u,v) in valid_pairs:
			if dist[u] + E[u][v] < dist[v]:
				dist[v] = dist[u] + E[u][v]
				pred[v] = u

	# return the unique negative cycles
	negative_cycles = {}
	for (u,v) in valid_pairs:
		if dist[u] + E[u][v] < dist[v]:

			cycle = [v]
			while len(cycle) == len(set(cycle)):
				cycle.append(pred[cycle[-1]])

			if cycle[0] == cycle[-1] and len(cycle) > 1:
				negative_cycles[str(set(cycle))] = cycle

			i = 1
			while cycle[i] != cycle[-1]: i += 1
			if len(cycle[i:]) > 1:
				negative_cycles[str(set(cycle[i:]))] = cycle[i:]

	return negative_cycles.values()

def find_arbitrage():

	# fetch
	u = urllib.urlopen('http://fx.priceonomics.com/v1/rates/')
	data = json.loads(u.read())

	# build graph
	E = {'_' : {}}
	for pair in data.keys():
		front, back = pair.strip().split('_')
		if front == back: continue
		if not E.has_key(front): E[front] = {}
		E[front][back] = -log(float(data[pair]))
	V = E.keys()
	for v in V: E['_'][v] = 0

	arbs = _bf(E.keys(), E, '_')

	# display
	for arb in arbs:
		seq = [(arb[i], arb[i+1]) for i in range(len(arb)-1)]
		print ''.ljust(80,'*')
		print 'ARBITRAGE OPPORTUNITY:', string.join(arb, '->').ljust(31),\
			datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S (UTC)')
		print ''.ljust(80,'*')
		x = 1
		for i in range(len(seq)):
			front, back = seq[i]
			y = x * float(data['%s_%s'%(front, back)])
			sell = "SELL %s %s" % (x, front)
			buy = " BUY %s %s" % (y, back)
			print sell.ljust(25) + buy.ljust(25) + "[Rate %s = %s]" % ('%s_%s'%(front, back), data['%s_%s'%(front, back)])
			x = y
		print "PROFIT = %s %s" %(x-1, arb[0])
	print ''.ljust(80,'*')

if __name__ == '__main__':

	find_arbitrage()
