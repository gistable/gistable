import random

def find_word():
    with open('words.txt', 'r') as f:
      lines = f.read().split()
    word = random.choice(lines)
    return word

def characters(word):
    chars = 0
    for char in word:
        chars += 1
    return chars

def game(word):
    chars = characters(word)
    blank = '_ ' * chars
    while '_ ' in blank:
        print(blank)
        guess = input('Guess a letter: ')
        if guess in word:
            blank.replace('_ ', guess)
        else:
            print('Incorrect!')
        print(word)

def main():
    print('Welcome to Hangman')
    word = find_word()
    print(word)
    game(word)

if __name__ == "__main__":
    main()