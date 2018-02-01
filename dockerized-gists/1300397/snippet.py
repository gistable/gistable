import array

def ilist_to_str(list):
    '''Integer list to string.'''
    return array.array('B', list).tostring()

def str_to_ilist(string):
    '''String to integer list'''
    return array.array('b', string).tolist()

def boodict_to_list(dict):
    '''From boolean dict to a list with only true values.'''
    return filter(None, [ k if v else None for k,v in dict.items()])

def split_list(s, d=','):
    '''Split and strip a list of string at deliminator.'''
    return [x.strip() for x in s.split(d)]

def strip_list(l):
    '''Strip a list of string of extra whitespace.'''
    return([x.strip() for x in l])

def strip_blank_str(str_list):
    '''Remove empty string from list'''
    return filter(None, str_list)

def unique(a):
    """ return the list with duplicate elements removed """
    return list(set(a))

def intersect(a, b):
    """ return the intersection of two lists """
    return list(set(a) & set(b))

def union(a, b):
    """ return the union of two lists """
    return list(set(a) | set(b))

def difference(a, b):
    """ show whats in list b which isn't in list a """
    return list(set(b).difference(set(a)))

def percent(a,b, r=2):
    try:
        return round(float(a)/float(b) * 100, r)
    except:
        return 0

def p_rents():
    import inspect
    print " << ".join([i[3] for i in inspect.stack()[1:-4]])