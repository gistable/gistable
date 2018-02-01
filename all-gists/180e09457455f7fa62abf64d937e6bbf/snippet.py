alphabet = 'abcdefghiklmnopqrstuvwxyz' # alphabet i/j exchangeable

def make_matrix(key):
	letters = ''
	for l in key:
		if l not in letters: letters += l

	for l in alphabet:
		if l not in letters: letters += l
	
	#print letters

	matrix = []
	row = []
	i = 0
	for l in letters:
		row.append(l)
		i += 1
		if i == 5:
			i = 0
			matrix.append(row)
			row = []

	return matrix



keyword = 'kilimanjaro'
matrix = make_matrix(keyword)

#print matrix
for x in range(5):
	print ''
	for y in range(5):
		print matrix[x][y], '',
		pass
	
print ''
print '--------------'