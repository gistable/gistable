#!/usr/bin/env python

"""
Example of how you can test if strings are anagrams 

"""

def is_anagram(str1, str2):
    """ 
    Check if str1 is an anagram of str2

    Keyword arguments:
    str1 - Input string 1
    str2 - Input string 2
    """
    # Strip whitespace
    updated_str1 = "".join(str1.split(" "))
    updated_str2 = "".join(str2.split(" "))

    # Sort strings
    updated_str1 = "".join(sorted(updated_str1))
    updated_str2 = "".join(sorted(updated_str2))

    # Test for equality
    return updated_str1 == updated_str2

def main():
    """ 
    Main

    """
    print(is_anagram("a man a plan a canal panama", "abc"))
    print(is_anagram("doggy", "y dogg"))

if '__main__' == __name__:
    main()
