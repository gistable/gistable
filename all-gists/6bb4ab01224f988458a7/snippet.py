import itertools

def is_sorted(l, comp = None):
        """
        Is the the list l  sorted, given the comparetor comp
        """
        if(len(l) == 2):
                if comp is None:
                        return l[0] < l[1]
                else:
                        return (comp(l[0], l[1]) < 1)
        if(len(l) == 1):
                return True
        else:
                # sorted if all sublists are sorted
                result = True
                for boolean in ([is_sorted(sub_l) for sub_l in all_subl(l)]):
                        result = boolean and result
                return result

def all_subl(l):
        """
        Returns a list of all sublists of l
        """
        length = len(l)
        for pattern in itertools.product(range(2), repeat = length):
                
                # skip empty, single or completely full soblists
                if (sum(pattern) == length) or (sum(pattern) <= 1):
                        continue

                yield [l[i] for i in xrange(length) if pattern[i]]

def sort(l, comp = None):
        """
        returns new sorted list
        """
        for order in itertools.permutations(l):
                if is_sorted(order, comp):
                        return order
