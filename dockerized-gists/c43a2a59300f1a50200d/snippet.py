#prob function toolkit

from decimal import *
#takes a decimal probability
def chance(choose, total):
	getcontext().prec = 6
	return float(Decimal(choose)/Decimal(total))
#checks probability of choosing elem from a lst.	
def occurence(elem, lst):
	getcontext().prec = 6
	size = lst.count(elem)
	return chance(size, len(lst))
	
def get_chances(lst):
    return {x:occurence(x, lst) for x in lst}
    
def best_chance(lst):
    dict = {occurence(x, lst):x for x in lst}
    return dict[max(dict.keys())]
