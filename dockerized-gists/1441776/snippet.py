
import sys

def can_make(word, letters):
	""" Return True if <word> can be generated using only the letters in the
	    list <letters>. """
	
	if len(word) > len(letters): return False
	
	l = letters[:]
	for index, letter in enumerate(word):
		if letter in l: l.remove(letter)
		else: return False
		
	return True


def main():
	with open(sys.argv[1]) as fh:
		dict_words = fh.read().split('\n')

	letters = sys.argv[2:]
	
	# <all_words> is the list of every word in list <dict_words> that can be
	# generated using the list of letters <letters>. <longest_words> is our
	# desired list of words.
	all_words = [w for w in dict_words if can_make(w, letters)]
	max_len = max(map(len, all_words))
	longest_words = [w for w in all_words if len(w) == max_len]
	print(longest_words)


if __name__ == '__main__':
	main()
