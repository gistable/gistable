"""
Implementation of the Gaussian Elimination Algorithm for finding the row-reduced echelon form of a given matrix.
No pivoting is done.
Requires Python 3 due to the different behaviour of the division operation in earlier versions of Python.
Released under the Public Domain (if you want it - you probably don't)
"""

def like_a_gauss(mat):
	"""
	Changes mat into Reduced Row-Echelon Form.
	"""
	# Let's do forward step first.
	# at the end of this for loop, the matrix is in Row-Echelon format.
	for i in range(min(len(mat), len(mat[0]))):
		# every iteration, ignore one more row and column
		for r in range(i, len(mat)):
			# find the first row with a nonzero entry in first column
			zero_row = mat[r][i] == 0
			if zero_row:
				continue
			# swap current row with first row
			mat[i], mat[r] = mat[r], mat[i]
			# add multiples of the new first row to lower rows so lower
			# entries of first column is zero
			first_row_first_col = mat[i][i]
			for rr in range(i + 1, len(mat)):
				this_row_first = mat[rr][i]
				scalarMultiple = -1 * this_row_first / first_row_first_col
				for cc in range(i, len(mat[0])):
					mat[rr][cc] += mat[i][cc] * scalarMultiple
			break

	# At the end of the forward step
	print(mat)
	# Now reduce
	for i in range(min(len(mat), len(mat[0])) - 1, -1, -1):
		# divide last non-zero row by first non-zero entry
		first_elem_col = -1
		first_elem = -1
		for c in range(len(mat[0])):
			if mat[i][c] == 0:
				continue
			if first_elem_col == -1:
				first_elem_col = c
				first_elem = mat[i][c]
			mat[i][c] /= first_elem
		# add multiples of this row so all numbers above the leading 1 is zero
		for r in range(i):
			this_row_above = mat[r][first_elem_col]
			scalarMultiple = -1 * this_row_above
			for cc in range(len(mat[0])):
				mat[r][cc] += mat[i][cc] * scalarMultiple
		# disregard this row and continue
	print(mat)


def augment_that_sucker(mat1, mat2):
	"""
	Duct-tape mat2's columns to the right of mat1
	Return a new matrix.
	"""
	retval = []
	for i in range(len(mat1)):
		r = mat1[i]
		newrow = r[:] + mat2[i]
		retval.append(newrow)
	return retval

def from_vector(vector):
	"""
	Convert a vector into a column matrix.
	"""
	retval = []
	for r in vector:
		retval.append([r])
	return retval

def transpose(mat):
	"""
	Return a transposed version of mat.
	"""
	retval = []
	for c in range(len(mat[0])):
		newrow = []
		for r in range(len(mat)):
			newrow.append(mat[r][c])
		retval.append(newrow)
	return retval

# testcase from http://reference.wolfram.com/mathematica/ref/RowReduce.html

mattest = [[1,2,3],[5,6,7],[7,8,9]]

mattest2 = from_vector([1,1,1])

mattest3 = augment_that_sucker(mattest, mattest2)			

like_a_gauss(mattest3)

print(transpose(mattest3)[3])