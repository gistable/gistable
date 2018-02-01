import fileinput

def find_min(a, x, length):
	if length == 0: return float('inf'), -1
	if len(a) == (x+1): return 1, 'out'
	h = reduce(lambda x, y: (a[y], y) if x[0] > a[y] else x, range(x+1, min(len(a), x+1+length)), (float('inf'), -1))
	return h[0]+1, h[1]

def find_min_hops(a):
	length = len(a)
	hops = [float('inf') for x in range(length)]
	index = [-1 for x in range(length)]

	for x in range(length-1, -1, -1):
		hops[x], index[x] = find_min(hops, x, a[x]) 
		# print hops[x], index[x]

	curr_index = 0
	if index[curr_index] == -1: 
		print 'failure'
		return
	print '0,', 
	while(index[curr_index] != 'out'):
		print str(index[curr_index])+',',
		curr_index = index[curr_index]
	print 'out'

# a = []
# for line in fileinput.input():
#     a.append(int(line.strip()))
# fileinput.close()

#ERRORS: 
# 1) reverse(range) was throwing up -> reversed(range) not reverse()
# OR range(len(a)-1, -1, -1)
# OR a = range(len(a)); a.reverse(); 
# 2) enumerate always starts from 0...even for enumerate(arr[4:7])
# Instead loop as i in range(4,7) ... use arr[i] inside
# 3) '+' doesnt work b/w int and str ...convert int to str by str()
# float('inf') as inf
# inputfile.input() takes argv[1:] all filenames items to iterate
# raw_input() for input() from user
#Use of reduce, filter, map, and list-comprehension


a = [1, 6, 0, 4, 2, 3, 1, 2, 0, 4]
find_min_hops(a)