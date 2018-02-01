def meme():
    word = raw_input("enter word: ")
    for c in word:
        print c.upper(), " ",
    print
    print
    for i, c in enumerate(word[1:-1]):
        print c.upper(), " " * ((len(word) - 1) * 4 - 3), word[len(word)-i-2].upper()
        print
    for c in word[::-1]:
        print c.upper(), " ",
    print
    print
    
meme()