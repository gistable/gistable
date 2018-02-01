import traceback
import re

def debug_var(a):
	s = traceback.extract_stack(limit=2)[0][3]
	g = re.match("\w+\((\w+)\)", s)
	print("%s = %r" % (g.group(1), a))

def main():
	foo=1
	debug_var(foo)

main()