import re
import random

def vtoc_idx(s):
  match_obj = re.search(r'[aeiou][^aeiou]', s.lower())
	if match_obj:
		return match_obj.start() + 1
	else:
		return None

def portnameteau(name_list):
	random.shuffle(name_list)
	s1 = name_list[0]
	s2 = name_list[1]
	end_s1 = vtoc_idx(s1)
	if end_s1 is None:
		end_s1 = len(s1)
	start_s2 = vtoc_idx(s2)
	if start_s2 is None:
		start_s2 = 0
	return (s1[:end_s1] + s2[start_s2:])

if __name__ == '__main__':

	import sys
	names = sys.argv[1:3]
	print portnameteau(names)

