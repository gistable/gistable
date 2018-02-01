def check_word(word, letters):
    """
    Check if a specific word can be created from the set of letters.
    """
    for w in word:
        pos = letters.find(w)
        if pos == -1:
            return False
        letters = letters[:pos] + letters[pos+1:]
    return True
    
def find_words(file, letters):
    """
    For a given dictinary file, find the longest words that can be created from
    the given set of letters.
    """
    words = []
    results = []
    longest = 0    
    
    for word in open(file):
        word = word.strip()
        if len(word) < longest:
            continue
        if check_word(word, letters):
            if len(word) > longest:
                longest = len(word)
                results = [word]
            else:
                results.append(word)
    return results
 
if __name__ == '__main__':
    
    import sys
    
    if len(sys.argv) < 3:
        print('Usage: scrabble.py dictionary [letter... ]')
        sys.exit()
    
    for r in find_words(sys.argv[1], str.join('', sys.argv[2:])):
        print(r)