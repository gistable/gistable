#!/usr/bin/env python
import sys

def netpromoterscore(scores):
	"""
	Calculates the netpromoter score of a list
	The Net Promoter Score is obtained by asking customers a single question on a 0 to 10 rating scale: 
	'How likely is it that you would recommend our company to a friend or colleague?' 
	Based on their responses, customers are categorized into one of three groups: 
	Promoters (9-10 rating), Passives (7-8 rating), and Detractors (0-6 rating). 
	
	NPS = # Promoters - # Detractors / # Votes * 100

	A score of 75 percent or above is considered quite high. NPS can be negative.
	
	>>> netpromoterscore([0,1,2,3,4,5,6,7,8,9,10])
	-45.45454545454545

	From http://www.measuringusability.com/blog/nps-ux.php:
	For example, 100 promoters and 30 passive and 80 detractors gets you a Net Promoter Score (NPS) of 9.5% (20 divided by 210). 
	This means there are 9.5 percent more promoters than detractors. 
	A NPS of -10 means you have 10 percent more detractors than promoters.
	>>> netpromoterscore( [9]*100 + [8]*30 + [4]*80 )
	9.523809523809524

	We should throw away any scores out side of 0-10
	>>> netpromoterscore( [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,-1,-2,-3,-4] )
	-45.45454545454545

	Not a list? I can't give you an NPS
	>>> netpromoterscore('no strings allowed')

	>>> netpromoterscore([])
	
	"""
	nps = None

	if hasattr(scores, '__iter__'):

		try:
			validscores = [v for v in scores if v>=0 and v <=10]

			promoters = [s for s in validscores if s >=9 and s <=10]
			detractors = [s for s in validscores if s >=0 and s <=6]
			nps = float(len(promoters) - len(detractors)) / len (validscores) * 100.0

		except ZeroDivisionError, e:
			pass

	return nps

def main(argv=None):
	if argv is None:
		argv = sys.argv

	# Your code here
	# Open a CSV file, extract out the NPS ratings

	# netpromoterscore(scores_iterable)

if __name__ == '__main__':
	import doctest
	doctest.testmod()
	
	sys.exit(main())