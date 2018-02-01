def clear_all():
	'''Erase all data, reseting the module'''
	global groups
	groups = dict()

def clear_collisions():
	pass
	
def clear_group(name):
	del groups[name]
	
def make_group(name):
	groups[name] = dict()
	groups[name]['shapes'] = dict()
	groups[name]['collision'] = dict()
	
def group_collision(group1_name, group2_name):
	group1 = groups[group1_name]
	group2 = groups[group2_name]
	if group2_name not in group1['collision'] and\
		 group1_name not in group2['collision']:
		print('Actually testing')
		for item1 in group1['shapes'].itervalues():
			for item2 in group2['shapes'].itervalues():
				if intersects(item1['shape'], item2['shape']):
					group1['collision'][group2_name] = True
					group2['collision'][group1_name] = True
					return True
		group1['collision'][group2_name] = False
		group2['collision'][group1_name] = False
		return False
	else:
		if group1_name in group2['collision']:
			return group2['collision'][group1_name]
		if group2_name in group1['collision']:
			return group1['collision'][group2_name]
		
def intersects(cir1, cir2):
	limit = (cir1['r']+cir2['r'])**2
	dist = (cir1['x']-cir2['x'])**2-(cir1['y']-cir2['y'])**2
	return dist < limit
	
	
def add_to_group(group_name, shape):
	groups[group_name]['shapes'][shape['name']] = {'shape':shape}
	
def circle(name, x, y, r):
	circle = dict()
	circle['name']=name
	circle['x']=x
	circle['y']=y
	circle['r']=r
	return circle
	
	
def foo_test():
	pass

	
	
	
if __name__ == '__main__':
	clear_all()
	make_group('test1')
	add_to_group('test1', circle('test_cir1',0,0,5))
	make_group('test2')
	add_to_group('test1', circle('test_cir2',10,0,6))
	
	print(group_collision('test1', 'test2'))
	print(group_collision('test1', 'test2'))
