def anagram_solve(letters, words):
    solution = [word.lower() for word in words if len(word) == len(letters)]

    for letter in letters:
        solution = [word for word in solution if letter in word and letters.count(letter) == word.count(letter)]

    return solution

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        print "Usage: %s [anagram]" % sys.argv[0]
    else:
        words = [word.rstrip() for word in file('/usr/share/dict/words', 'r')]

        for anagram in sys.argv[1:]:
            print "%s: %s" % (anagram, " ".join(anagram_solve(anagram, words)))