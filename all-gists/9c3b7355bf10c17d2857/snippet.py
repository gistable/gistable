#!/usr/bin/env python3

# Given a pattern and a list of filenames, return the filenames which match the given pattern in a separate list.
# The pattern should support two wild card characters '?' and '*', in which '?' can match one or zero character and '*'
# can match any number of characters

WILDCARD = '*'
ZERO_OR_ONE = '?'


def wildcard_match(string):
    """Matches the pattern '*' to the given string

    Generator which iterates through each character i of the string and yields the substring from the start of i.

    Args:
        string (str): Input string for '*' pattern to be matched against.

    Returns:
        str. Given string[N], yields each substring string[0:],..string[N:]
    """
    if not string:
        yield string
    else:
        for i in range(len(string)+1):
            yield string[i:]


def zero_or_one_match(string):
    """Attempts to match one or zero characters.

    Generator which returns the original string as well as string[1:].

    Args:
        string (str): Input string for '?' pattern to be matched against.

    Returns:
        str. Given string, yields string and string[1:]
    """
    if not string:
        yield string
    else:
        for i in range(2):
            yield string[i:]


def literal_match(literal, string):
    """Attempts to match to the literal parameter passed in

    Args:
        literal (str): String to be matched against.
        string (str): The input string

    Returns:
        bool. True if string matched to literal, False otherwise.
    """
    return True if literal in string[:len(literal)] else False

def single_match(pattern, filename):
    """ Determines if the filename matches with the pattern with the use of recursion.

    Args:
        pattern (str): Pattern to be matched against.
        filename (str): The filename to check to see if it matches with the passed in pattern.

    Return:
        bool. True if filename matches to the pattern, false if the filename does not
    """
    if not pattern:
        return True

    is_match = False
    current = pattern[0]
    tail = pattern[1:]
    if current == WILDCARD:
        for substring in wildcard_match(filename):
            if single_match(tail, substring):
                is_match = True
                break

    elif current == ZERO_OR_ONE:
        for substring in zero_or_one_match(filename):
            if single_match(tail, substring):
                is_match = True
                break
    else:
        for i in range(len(pattern)):
            if pattern[i] != WILDCARD and pattern[i] != ZERO_OR_ONE:
                continue
            else:
                current = pattern[:i]
                tail = pattern[i:]
                break

        if literal_match(current, filename):
            is_match = single_match(tail, filename)

    return is_match


def match(pattern, filenames):
    """Checks a list of strings to see if any of them matches with the passed in pattern

    Args:
        pattern (str): The pattern to be matched against
        filenames (list): List of strings to match

    Returns:
        list. A list containing a subset of the passed in filenames that matched with pattern
    """
    matching_filenames = []
    for filename in filenames:
        if single_match(pattern, filename):
            matching_filenames.append(filename)
    return matching_filenames


if __name__ == '__main__':
    print(["abcd", "dabc", "abc"] == match("?abc*", ["abcd", "dabc", "abc", "efabc", "eadd"]))
    print(["abcd", "dabc", "abc"] == match("?a**c*", ["abcd", "dabc", "abc", "efabc", "eadd"]))

