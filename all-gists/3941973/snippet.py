# 1. Word Scores
def getWordScore(word, n):
    return (len(word) * sum(SCRABBLE_LETTER_VALUES[x] for x in word)) + (50 if len(word) == n else 0)

# Test implementation
def getFrequencyDict(aStr):
    return dict((letter, aStr.count(letter)) for letter in aStr)
	
# 2. Dealing with hands
def updateHand(hand, word):
    return dict((a, b - word.count(a)) for a, b in hand.items())
	
# 3. Valid words
def isValidWord(word, hand, wordList):
    return word in wordList and all(hand.get(a, 0) >= b for a, b in getFrequencyDict(word).items())

# 4. Hand length
def calculateHandlen(hand):
    return sum(x for x in hand.values())

# 5. Playing a hand
def playHand(hand, wordList, n):
    totalScore = 0
    output = "Run out of letters."
    while calculateHandlen(hand) > 0:
        displayHand(hand)
        word = raw_input('Enter word, or a "." to indicate that you are finished: ').lower()
        if word == '.':
            output = "Goodbye!"
            break
        else:
            if not isValidWord(word, hand, wordList):
                print("Invalid word, please try again.")
            else:
                score = getWordScore(word, n)
                totalScore += score
                print('"{0:s}" earned {1:d} points. Total: {2:d} points.'.format(word, score, totalScore))
                hand = updateHand(hand, word)
    print('{0:s} Total score: {1:d} points.'.format(output, totalScore))

# 6. Playing a game
def playGame(wordList):
  hand = False
  while True:
      user = raw_input("Enter n to deal a new hand, r to replay the last hand, or e to end game: ").lower()
      if user not in 'nre':
          print("Invalid command.")
      else:
          if user == 'r' and not hand:
              print("You have not played a hand yet. Please play a new hand first!")
          elif user == 'n':
              hand = dealHand(HAND_SIZE)
              playHand(hand.copy(), wordList, HAND_SIZE)
          elif user == 'r' and hand:
              playHand(hand.copy(), wordList, HAND_SIZE)
          else:
              break
          print("")

# 7. Computer chooses a word
def compChooseWord(hand, wordList):
    return max([x if isValidWord(x, hand, [x]) else "" for x in wordList], 
               key=lambda x: getWordScore(x, HAND_SIZE)) or None
    