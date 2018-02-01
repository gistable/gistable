'''
The MIT License (MIT)

Copyright (c) 2013 Krishna Bharadwaj <krishna@krishnabharadwaj.info>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

WORDS = open('wordlist.txt').read().split()
KEYBRD_LAYOUT = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']

def match(path, word):
    """ Checks if a word is present in a path or not. """

    try:
        for char in word:
            path = path.split(char, 1)[1]
        return True
    except : return False

def get_keyboard_row( char ):
    """ Returns the row number of the character """

    for row_no, row in enumerate(KEYBRD_LAYOUT):
        if char in row:
            return row_no

def compress(sequence):
    """ Removes redundant sequential characters. ex : 11123311 => 1231 """
    ret_val = [ sequence[0] ]
    for element in sequence:
        if ret_val[-1] != element:
            ret_val.append(element)
    return ret_val

def get_minimum_wordlength(path):
    """ 
    Returns the minimum possible word length from the path.
    Uses the number of transitions from different rows in 
    the keyboard layout to determin the minimum length
    """
    row_numbers = map(get_keyboard_row, path)
    compressed_row_numbers = compress(row_numbers)
    return len(compressed_row_numbers) - 3

def get_suggestion(path):
    """ Returns suggestions for a given path. """

    suggestions = filter(lambda x: x[0] == path[0] and x[-1] == path[-1], WORDS)
    suggestions = filter(lambda x: match(path, x), suggestions)

    min_length = get_minimum_wordlength(path)
    suggestions = filter(lambda x: len(x) > min_length, suggestions)

    return suggestions

if __name__ == '__main__':
    test_cases = ['heqerqllo',                   # hello
        'qwertyuihgfcvbnjk',                     # quick
        'wertyuioiuytrtghjklkjhgfd',             # world
        'dfghjioijhgvcftyuioiuytr',              # doctor
        'aserfcvghjiuytedcftyuytre',             # architecture
        'asdfgrtyuijhvcvghuiklkjuytyuytre',      # agriculture
        'mjuytfdsdftyuiuhgvc',                   # music
        'vghjioiuhgvcxsasdvbhuiklkjhgfdsaserty', # vocabulary 
        ]

    for test in test_cases:
        print get_suggestion(test)