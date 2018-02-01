def OddOrEven ():

    try:
        num = int(input("This program can tell if the number that you write is odd or even. Write your number now "))
        if num % 2 == 0:
            print ("That number is even!")

            playagain = input("Would you like to play again? y/n? ")

            if playagain == "y":

                OddOrEven()

            else:
                input("Thanks for playing! Come again soon! Press enter to close.")

                exit()

        if num % 2 != 0:
            print("That number is odd!")

            playagain = input("Would you like to play again? y/n? ")

            if playagain == "y":

                OddOrEven()

            else:
                input("Thanks for playing! Come again soon! Press enter to close.")

                exit()

    except ValueError:
        print("Woops, I don't understand that! Try again!")
        OddOrEven()


OddOrEven()
