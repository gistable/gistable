from __future__ import print_function
ambidict = {'R' : {'A', 'T'}, 'Y' : {'C', 'G'} }
def getNearbyChars(nt): return ambidict.get(nt, nt)

def nearbyPermutations(letters,index=0):
    if (index >= len(letters)): return set([''])
    subWords = nearbyPermutations(letters, index + 1)
    nearbyLetters = getNearbyChars(letters[index])
    return permutations(subWords, nearbyLetters)

def  permutations(subWords, nearbyLetters):
   permutations = set()
   for subWord in subWords:
       for letter in nearbyLetters:
           permutations.add(letter + subWord)
   return permutations

if __name__ == '__main__':
    import sys
    print(nearbyPermutations(sys.argv[1]))

