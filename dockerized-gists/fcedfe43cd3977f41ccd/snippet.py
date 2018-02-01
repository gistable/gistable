from operator import itemgetter

def inefficient_most_common(d, n):
    """
    Returns the n most common words in a dictionary.
    
    Args:
        d: A dictionary of the frequencies or counts.
        n: An integer representing the number of words to be returned.

    Returns the n most common words in d.
    """
    return [i[0] for i in sorted(d.items(), key=itemgetter(1), reverse=True)[:n]]

def more_efficient_most_common(d, n):
    """
    Returns the n most common words in a dictionary. Has O(nm) performance. Note
    this can be made to make n less calls 
    
    Args:
        d: A dictionary of the frequencies or counts.
        n: An integer representing the number of words to be returned.

    Returns a list of the n most common words in d.
    """
    if n <= 0:
        return []
    items = d.items()
    most_common_items = []
    
    # The complexity in range handles the case where n is less then the number
    # of entries in the dictionary.
    for i in range(n if n < len(items) and n > 0 else len(items)):
        # This could be faster by writing a max method that also poped the best
        # item. It goes from T(n) = 2n * mc to n * mc where c is some constant
        # factor, n is len(d) and m is the n most common words.
        most_common_item = max(items, key=itemgetter(1))
        items.remove(most_common_item)
        most_common_items.append(most_common_item[0])
    return most_common_items