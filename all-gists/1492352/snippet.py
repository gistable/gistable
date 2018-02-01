"""
This code is for part one the AI Class optional Natural Language Processing
programming assignment. See youtu.be/KuSg1wcty3s for the complete problem
definition.

We are given a string which has been encoded with a Caesar cipher:
http://en.wikipedia.org/wiki/Caesar_cipher, and our job is to decode it.
You could do this by brute force, simply print out each shift of the letters
and look for the correct one by eye.

However, a much nicer idea is to implement a language model so that your
computer program can decide whether the decoded string looks like regular
English and only print the strings that pass your test.

For this program my language model is simple: each word must contain a vowel.

The encoded string is:

esp qtcde nzyqpcpynp zy esp ezatn zq lcetqtntlw tyepwwtrpynp hld 
spwo le olcexzfes nzwwprp ty estd jplc

The string decodes to:

the first conference on the topic of artificial intelligence was 
held at dartmouth college in this year

See http://www.livinginternet.com/i/ii_ai.htm for the answer.


To run this program simply type 'python nlp1.py' at the command line.

Author
------
@jiffyclub
git.io/jiffyclub

"""

import string

S = """esp qtcde nzyqpcpynp zy esp ezatn zq lcetqtntlw tyepwwtrpynp hld 
spwo le olcexzfes nzwwprp ty estd jplc"""

VOWELS = "aeiou"


def make_trans(n):
    """
    Make a translation by shifting string.lowercase `n` places to the left.
    
    Parameters
    ----------
    n : int
        Number of places to shift the alphabet.
    
    Returns
    -------
    Translation table made by `string.maketrans`.
    
    """
    new_lowercase = string.lowercase[n:] + string.lowercase[:n]
    
    return string.maketrans(string.lowercase, new_lowercase)
    
    
def translate(s,n):
    """
    Decode a string `s` using a cipher that shifts the alphabet
    `n` places to the left.
    
    Parameters
    ----------
    s : str
        String to be decoded.
    
    n : int
        Number of places to shift the alphabet for shift cipher.
    
    Returns
    -------
    d : str
        Decoded string.
    
    """
    trans = make_trans(n)
    
    return string.translate(s, trans)


def check_for_vowels(s):
    """
    Split a string on spaces and check that every word contains
    a vowel ('aeiou'). Returns True if every word contains a vowel,
    False otherwise.
    
    Parameters
    ----------
    s : str
        String to check.
    
    Returns
    -------
    all : bool
        True if every word contains vowels, False otherwise.
    
    """
    split = s.split()
    
    for word in split:
        num = len([c for c in word if c in VOWELS])
        
        if num == 0:
            return False
    
    return True


def main():
    """
    Go through all shifts of the alphabet and print the decoded S for
    shifts that result in cases where every word contains a vowel.
    
    """
    for i in range(26):
        s = translate(S, i)
        
        if check_for_vowels(s):
            print s


if __name__ == '__main__':
    main()
