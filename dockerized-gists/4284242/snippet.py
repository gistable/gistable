#encoding:utf8

def analyze(filename):
	statics = {}
	with open(filename) as fh:
		for line in fh:
			infos = line.split()
			obj_name, obj_size, _, refs = infos[0:4]
			statics[obj_name] = [int(refs), int(obj_size)]
	return statics

def gen_diff(staticsA, staticsB):
	diff = {}
	new = {}
	for obj_name, recordB in staticsB.iteritems():
		if not staticsA.has_key(obj_name):
			new[obj_name] = recordB
			continue
		recordA = staticsA[obj_name]
		if recordB != recordA:
			diff[obj_name] = [recordB[0] - recordA[0], recordB[1] - recordA[1]]
	return diff, new

def gen_ref_report(diff):
	for obj_name in sorted(diff.iterkeys()):
		record = diff[obj_name]
		ref, size = record
		if (ref > 0):
			print "obj ", obj_name, "amount increase:", str(ref)

def gen_size_report(diff):
	for obj_name in sorted(diff.iterkeys()):
		record = diff[obj_name]
		ref, size = record
		if (size > 0):
			print "obj ", obj_name, "size increase:", str(size)

def gen_new_report(new):
	for obj_name in sorted(new.iterkeys()):
		record = new[obj_name]
		print "new obj:", obj_name, " ref:", record[0], " size:", record[1]

def print_time_diff(filename1, filename2):
	import os.path, datetime
	timestamp1 = os.path.getmtime(filename1)
	timestamp2 = os.path.getmtime(filename2)
	delta = datetime.timedelta(seconds = (timestamp2 - timestamp1))
	print "=" * 10, "In", delta, "=" * 10

def main(filename1, filename2):
	print_time_diff(filename1, filename2)
	staticsA = analyze(filename1)
	staticsB = analyze(filename2)
	diff, new = gen_diff(staticsA, staticsB)
	gen_ref_report(diff)
	gen_size_report(diff)
	gen_new_report(new)

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description="gen diff from two obj_dump file")
	parser.add_argument("pathA", metavar="PATHA", type=str)
	parser.add_argument("pathB", metavar="PATHB", type=str)
	args = parser.parse_args()
	main(args.pathA, args.pathB)
