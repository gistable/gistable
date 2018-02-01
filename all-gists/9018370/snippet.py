# -*- coding: utf-8 -*-
'''
Frequent Words with Mismatches Problem: Find the most frequent k-mers with mismatches in a string.
Input: A string Text as well as integers k and d. (You may assume k ≤ 12 and d ≤ 3.)
Output: All most frequent k-mers with up to d mismatches in Text.
'''
from collections import OrderedDict
from operator import itemgetter

def kmers_finder_with_mismatches(sequence, motif_length, max_mismatches, most_common=False):
	'''(str, int, int) -> sorted(list)
	Find the most frequent k-mers with mismatches in a string.
	Input: A sequence and a pair of integers: motif_length (<=12) and max_mismatch (<= 3).
	Output: An OrderedDict containing all k-mers with up to d mismatches in string.
	If most_common: return only the most represented kmer(s).
	Sample Input:	ACGTTGCATGTCGCATGATGCATGAGAGCT 4 1
	Sample Output:	OrderedDict([('ATGC', 5), ('ATGT', 5), ('GATG', 5),...])
	'''

	#check passed variables
	if not motif_length <= 12 and motif_length >= 1:
		raise ValueError("motif_length must be between 0 and 12. {} was passed.".format(motif_length))
	if not max_mismatches <= 3 and max_mismatches >= 1:
		raise ValueError("max_mismatch must be between 0 and 3. {} was passed.".format(max_mismatches))

	#build a dict of motifs/kmers
	motif_dict = {}
	for i in range(len(sequence) - motif_length +1):
		motif = sequence[i:i+motif_length]
		if motif not in motif_dict:
			motif_dict[motif] = 1
		else:
			motif_dict[motif] += 1

	#check for mismatches
	motif_dict_with_mismatches = {}
	for kmer in motif_dict:
		motif_dict_with_mismatches.update({kmer:[]})
			
		for other_kmer in motif_dict:
			mismatches = 0
			for i in range(len(kmer)):
				if kmer[i] != other_kmer[i]:
					mismatches += 1
			if mismatches <= max_mismatches:
				motif_dict_with_mismatches[kmer].append([other_kmer,motif_dict[other_kmer]])

	#count occurrences of motifs
	tmp = {}
	for item in motif_dict_with_mismatches:
		count = 0
		for motif in motif_dict_with_mismatches[item]:
			count += motif[-1]
		tmp.update({item:count})

	result = OrderedDict(sorted(tmp.items(), key=itemgetter(1), reverse=True))
	
	#find the most common/s
	if most_common:
		commons = OrderedDict()
		_max = result.items()[0][1]
		for item in result:
			if result[item] == _max:
				commons.update({item:result[item]})
			else:
				return commons

	return result


##Test
sequence = 'CACAGTAGGCGCCGGCACACACAGCCCCGGGCCCCGGGCCGCCCCGGGCCGGCGGCCGCCGGCGCCGGCACACCGGCACAGCCGTACCGGCACAGTAGTACCGGCCGGCCGGCACACCGGCACACCGGGTACACACCGGGGCGCACACACAGGCGGGCGCCGGGCCCCGGGCCGTACCGGGCCGCCGGCGGCCCACAGGCGCCGGCACAGTACCGGCACACACAGTAGCCCACACACAGGCGGGCGGTAGCCGGCGCACACACACACAGTAGGCGCACAGCCGCCCACACACACCGGCCGGCCGGCACAGGCGGGCGGGCGCACACACACCGGCACAGTAGTAGGCGGCCGGCGCACAGCC'
motif_length = 10
max_mismatches = 2
a = kmers_finder_with_mismatches(sequence, motif_length, max_mismatches, most_common=False)
for key in a:
	print key, a[key]

