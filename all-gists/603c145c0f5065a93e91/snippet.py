# Rock paper scissors using modulus arithmetic. The time.sleep() functions
# are added in to give the output a bit more readability , rather than
# flooding the screen all at once, it allows user to parse information
import random, time

shapes = ['Rock', 'Paper', 'Scissors']
wins = 0
losses = 0
ties = 0

while True:
# Display choices
    for item,shape in enumerate(shapes):
        print '{0}. {1}'.format(item+1, shape)
    # Get user input, testing whether or not it's valid (converting to int if
    # user doesn't input int will throw ValueError exception), then subtract 1
    # since display is 1-3 while indexes are 0-2
    while True:
        try:
            userChoice = raw_input('Choose shape [1-3]: ')
            userChoice = int(userChoice) - 1
        except ValueError:
            print 'Invalid input, single-digit numbers only.'
        if 0 <= userChoice <= 2:
            break
        else:
            print 'Invalid option - number from 1 to 3 only.'
    # Generate computer's choice
    computerChoice = random.randrange(0, len(shapes))
    print '\nUser:     ', shapes[userChoice]
    print 'Computer: ', shapes[computerChoice]
    time.sleep(2)
    # Get difference in choices for use with modulo arithmetic:
    # if the difference in choices is 0, they are the same, if
    # the difference (mod 3) is 1, Player 1 wins, and if it'
    # 2, then Player 2 wins
    choiceDifference = userChoice - computerChoice
    # modulo arithmetic
    if choiceDifference == 0:
        print '\nGame is a tie.'
        ties += 1
    else:
        if (choiceDifference % 3) == 1:
            print '\nYou win! {0} defeats {1}.'.format(shapes[userChoice], 
                shapes[computerChoice])
            wins += 1
        elif(choiceDifference % 3) == 2:
            print '\nYou lose. {0} defeats {1}.'.format(shapes[computerChoice], 
                shapes[userChoice])
            losses += 1
    time.sleep(1)
    # Output scores
    print '\nWins:   ', wins
    print 'Losses: ', losses
    print 'Ties:   ', ties
    time.sleep(1)
    # Ask user if they want to play again, checking for valid input by checking
    # whether or not the user entered a string, and then if the string lowercased
    # isn't 'y' or 'n', it's invalid (user tries again).
    while True:
        playAgain = raw_input('Play again [y/n]: ')
        if isinstance(playAgain, str):
            if playAgain.lower() == 'y':
                break
            elif playAgain.lower() == 'n':
                exit()
            else:
                print 'Invalid input. Enter Y or N.'
        else:
            print 'Invalid input. Enter Y or N.'
