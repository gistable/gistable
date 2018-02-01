def anagram(string1, string2, ignore_whitespace=False):
    """Determines whether two strings are anagrams."""
    if ignore_whitespace==True:
        import re
        string1, string2 = re.sub('\s', '', string1), re.sub('\s', '', string2)
    if len(string1) != len(string2): return False
    list1, list2 = [c for c in string1].sort(), [c for c in string2].sort()
    if list1 != list2: return False
    return True