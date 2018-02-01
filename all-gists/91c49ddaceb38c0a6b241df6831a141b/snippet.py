import random, math

#Ignore def monte_carlo(): ...im just defining a function
def monte_carlo():
    #At the end sums will add up all the f(n)
    sums = 0

    #just creating a dictionary, ignore this, not too important
    functions = {'1': 'x', '2': 'x^2', '3': 'sin', '4': 'cos', '5': 'exp'}

    print("Choose your function")

    #This is just a print of all available functions to chose...ignore it!
    choice = input("""Enter 1 for: f(x) =  x
Enter 2 for: f(x) = x^2
Enter 3 for: f(x) = sin(x)
Enter 4 for: f(x) = cos(x)
Enter 5 for: f(x) = exp(x)

Choose your function:  """)

    #Just creating a list of options
    valid_options = ['1', '2', '3', '4', '5']

    #if user does not type any of the options from 1 to 5 (above list) then terminate programme
    if choice not in valid_options:
        print("Enter a valid option next time. \n")
        return 0

    #otherwise carry on with programme
    else:
        #this asks user for the number of simulations
        no_of_simulations = input('Enter the number of similations: ')

        #if user types in anything
        if no_of_simulations:

            #terminate the programme if user typed in a negative number or any jibberish!
            if not no_of_simulations.isdigit():
                print("Please enter a valid number next time \n")
                return 0

            #if user types in positive number then carry on
            else:
                #ask user for the number of simulations
                no_of_simulations = int(no_of_simulations)

                #this will itterate through 0, 1, 2, 3,...,no_of_simulations
                #so num = 0,1,2,3... etc
                for num in range(no_of_simulations):

                    #this gives new random number everytime num updates
                    random_num = random.uniform(0,1)

                    #This if statement is basically saying if user picked sin(x), cos(x) or exp(x)
                    if int(choice) >= 3:

                        #result is basically f(x). E.g. if your random number is 0.4 and
                        # you picked sin(x) then result will calculate sin(0.4)
                        # result will be
                        result = eval('math.%s(%s)' % (functions.get(choice), random_num))

                        #This sums adds the results. E.g. if user picked 2 for number of simulations
                        #then you will generate 2 random numbers say 0.4 and 0.2.
                        #then sums = sin(0.4) + sin(0.2)
                        sums += result

                    #If user picked x^2 then...
                    elif int(choice) == 2:
                        result = random_num * random_num
                        sums += result

                    #If user picked x then...
                    elif int(choice) == 1:
                        sums += random_num

                #this is just dividing by n.
                print(float(sums/no_of_simulations))


monte_carlo()
