import string

# 1. Polynomials
def evaluatePoly(poly, x):
    return float(sum(b * (x ** a) for a,b in enumerate(poly)))  

# 2. Derivatives
def computeDeriv(poly):
    return [float (a * b) for a, b in enumerate(poly)][1:] or [0.0]

# 3. Newton's method
def computeRoot(poly, x_0, epsilon):
    iterations = 0
    evalPoly = evaluatePoly(poly, x_0)
    deriv = computeDeriv(poly)
    while abs(evalPoly) > epsilon:
        x_0 -= (evalPoly / evaluatePoly(deriv, x_0))
        evalPoly = evaluatePoly(poly, x_0)
        iterations += 1
    return [float(x_0), iterations]

# 4. a) Is the word guessed?
def isWordGuessed(secretWord, lettersGuessed):
    all(letter in lettersGuessed for letter in secretWord)

# 4. b) Printing out the user's guess
def getGuessedWord(secretWord, lettersGuessed):
    return " ".join([letter if letter in lettersGuessed else "_" for letter in secretWord])

# 4. c) Printing out all available letters
def getAvailableLetters(lettersGuessed):
    return "".join([letter if letter not in lettersGuessed else "" for letter in string.ascii_lowercase])

# 5. Hangman - the game
def hangman(secretWord):
    print("Welcome to the game Hangman!")
    print("I am thinking of a word that is {0:d} letters long".format(len(secretWord)))
    gameOver = False
    guessesLeft = 8
    lettersGuessed = []
    while not gameOver:
        print("-" * 11)
        print("You have {0:d} guesses left".format(guessesLeft))
        availableLetters = getAvailableLetters(lettersGuessed)
        print("Available Letters: {0:s}".format(availableLetters))
        guess = raw_input("Please guess a letter: ")
        guess = guess[0].lower()
        if guess in availableLetters:
            lettersGuessed.append(guess)
            if guess in secretWord:
                response = "Good guess:"
                if isWordGuessed(secretWord, lettersGuessed):
                    gameOver = True
            else:
                guessesLeft -= 1
                response = "Oops! That letter is not in my word:"
                if guessesLeft == 0:
                    gameOver = True
        else:
            response = "Oops! You've already guessed that letter:"
        print("{0:s} {1:s}".format(response, getGuessedWord(secretWord, lettersGuessed)))
    print("-" * 11)
    if isWordGuessed(secretWord, lettersGuessed):
        print("Congratulations, you won!")
    else:
         print("Sorry, you ran out of guesses. The word was {0:s}.".format(secretWord))