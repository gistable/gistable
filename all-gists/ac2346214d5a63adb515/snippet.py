#takes a string, and for every time a certain character appears, will create a slice of itnd append it to a list.

def string_indexer(string, value):
# returns all indexes for which a value appears in a string
	indices, istring = [], list(string)
	for s in istring:
		if s == value:
			indices.append(istring.index(s))
			istring[istring.index(s)] ='X'
	return indices
def set_string_indexer(string, set):
# returns all indexes for which a value in a set appears in a string, in the
#form of a multidict
	indices, istring = {x:[] for x in set}, list(string)
	for s in istring:
		if s in set:
			indices[s].append(istring.index(s))
			istring[istring.index(s)] ='X'
	return indices
