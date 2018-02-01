import re

myfile = open('list', 'r')

callnos = myfile.readlines()

p = re.compile("""^(?P<aclass>[A-Z]{1,3})
		  (?P<nclass>\\d{1,4})(\\ ?)
		  (\\.(?P<dclass>\\d{1,3}))?
		  (?P<date>\\ [A-Za-z0-9]{1,4}\\ )?
		  ([\\ \\.](?P<c1>[A-Z][0-9]{1,4}))
		  (\\ (?P<c1d>[A-Za-z0-9]{0,4}))?
		  (\\.?(?P<c2>[A-Z][0-9]{1,4}))?
		  (\\ (?P<e8>\\w*)\\ ?)?
       		  (\\ (?P<e9>\\w*)\\ ?)?
		  (\\ (?P<e10>\\w*)\\ ?)?""",
		  re.VERBOSE)

def ncmp(x,y):
	if x is None and y is None:
		return 0
	if x is None:
		return -1
	if y is None:
		return 1
	x = int(x)
	y = int(y)
	return cmp(x,y)

def sortfunc(x, y):
	xp = p.search(x)
	yp = p.search(y)
	parts = {'aclass':cmp,'nclass':ncmp,'dclass':ncmp,'date':cmp,'c1':cmp,'c1d':cmp,'c2':cmp,'e8':cmp,'e9':cmp,'e10':cmp}
	for part in parts:
		cr = parts[part](xp.group(part),yp.group(part))
		if cr != 0:
			return cr

def normalize(callno):
	cp = p.search(callno)
	out = cp.group('aclass') + cp.group('nclass')
	if cp.group('dclass') is not None:
		out += "."+cp.group('dclass')
	if cp.group('date') is not None:
                out += " "+cp.group('dclass')+ " "
	out += "."+cp.group('c1')
	if cp.group('c1d') is not None:
                out += " "+cp.group('c1d')+ " "
	if cp.group('c2') is not None:
		out += " "+cp.group('c2')
	if cp.group('e8') is not None:
                out += " "+cp.group('e8')
	if cp.group('e9') is not None:
                out += " "+cp.group('e9')
	if cp.group('e10') is not None:
                out += " "+cp.group('e10')
	return out

callnos.sort(sortfunc)

for callno in callnos:
	print "%25s %25s" % (callno.strip(), normalize(callno).strip())