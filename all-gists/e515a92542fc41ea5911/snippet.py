import math

def stringNorm(s):
    norm = 0
    for c in s:
        if not c==" ":
            norm+=math.pow(ord(c),2)
    return math.sqrt(norm)

def anagram_detection(s1,s2):
    return stringNorm(s1)==stringNorm(s2)

s1 = input("Please enter first string:  ").lower()
s2 = input("Please enter second string: ").lower()


print ("Anagram.") if anagram_detection(s1,s2) else print ("Not Anagram.")