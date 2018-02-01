#python
import lx
import lx.symbol as symbols

# Save this into your MODO scripts directory.

# Example usage:

# Find symbols with value of enable
# import symbolUtils as su
# su.find('enable', printOut=True)

# Find symbols with value containing enable
# import symbolUtils as su
# su.contains('enable', printOut=True)

# Find symbols containing ENABLE
# import symbolUtils as su
# su.findSymbols('ENABLE', printOut=True)


def find(value, ignoreCase=False, printOut=False, withlxsymbol=False):
	res = []
	if ignoreCase:
		res = [x for x in dir(symbols) if value.lower() == getattr(symbols, x).lower()]
	else:
		res = [x for x in dir(symbols) if value == getattr(symbols, x)]
	if printOut:
		printList(res, withlxsymbol)
	return res

def contains(value, ignoreCase=False, printOut=False, withlxsymbol=False):
	res = []
	if ignoreCase:
		res = [x for x in dir(symbols) if value.lower() in getattr(symbols, x).lower()]
	else:
		res = [x for x in dir(symbols) if value in getattr(symbols, x)]
	if printOut:
		printList(res, withlxsymbol)
	return res

def findSymbols(value, ignoreCase=False, printOut=False, withlxsymbol=False):
	res = []
	if ignoreCase:
		res = [x for x in dir(symbols) if value.lower() in x.lower()]
	else:
		res = [x for x in dir(symbols) if value in x]
	if printOut:
		printList(res, withlxsymbol)
	return res

def printList(entries, withlxsymbol=False):
	if withlxsymbol:
		print '\nlx.symbol.'.join(entries)
	else:
		print '\n'.join(entries)