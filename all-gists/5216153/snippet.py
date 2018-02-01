# load up words into a set
with open('words', 'r') as f:
    words = f.readlines()

# sanitize words (removing \n at the end)
words = set([word[:-1] for word in words])


# returns all possible words from the starting of the line
def beginWords(string):
    for i in range(0, len(string)+1):
        if i < 45 and string[:i].upper() in words:
            yield (string[:i], i)


def allPossibilities(string):
    def solve(s, phrase, sentences):
        if len(s) == 0:
            sentences += [' '.join(phrase)]

        for word, l in beginWords(s):
            solve(s[l:], phrase + [word], sentences)

    sentences = []
    solve(string, [], sentences)
    return sentences


import sys
if __name__ == '__main__':
    if len(sys.argv) != 1:
        results = allPossibilities(sys.argv[1])
    else:
        string = raw_input("Enter string : ")
        results = allPossibilities(string)

    print "%d possibilities\n" % len(results)
    print '\n'.join(results)
