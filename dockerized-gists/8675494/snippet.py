'''
Minimum Skew Problem: Find a position in a genome minimizing the skew.
     Input: A DNA string Genome.
     Output: All integer(s) i minimizing Skewi (Genome) among all values of i (from 0 to |Genome|).

CODE CHALLENGE: Solve the Minimum Skew Problem.
Sample Input:
     TAAAGACTGCCGAGAGGCCAACACGAGTGCTAGAACGAGGGGCGTAAACGCGGGTCCGAT

Sample Output:
     11 24


'''

sequence = 'TAAAGACTGCCGAGAGGCCAACACGAGTGCTAGAACGAGGGGCGTAAACGCGGGTCCGAT'

def skew(sequence):
	c = 0
	g = 0
	min_skew = 0
	skew_list = []
	index = 0
	for i in sequence:
		index += 1
		if i == 'C':
			c += 1
		if i == 'G':
			g += 1
		skew = g-c
		if skew < min_skew:
			skew_list = [index]
			min_skew = skew
		if skew == min_skew and index not in skew_list:
			skew_list.append(index)	
	print(skew_list)
	
#with open('data.txt', 'r') as in_file:
	#sequence = in_file.readline()	
	#skew(sequence)
skew(sequence)
