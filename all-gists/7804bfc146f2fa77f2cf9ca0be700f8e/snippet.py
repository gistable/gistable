def Calculate(firstNumber, secondNumber):
    statement = input("Would you like to {/|*|+|-}")
    if statement == "/":
        answer = firstNumber / secondNumber
        print(answer)
        GetNumbers()
    if statement == "*":
        answer = firstNumber * secondNumber
        print(answer)
        GetNumbers()
    if statement == "+":
        answer = firstNumber + secondNumber
        print(answer)
        GetNumbers()
    if statement == "-":
        answer = firstNumber - secondNumber
        print(answer)
        GetNumbers()
    else:
        print("That was not one of the options.")
        Calculate(firstNumber, secondNumber)

def GetNumbers():
    firstNumber = int(input("Please enter the first number(integers only):"))
    secondNumber = int(input("Please enter the second number(integers only):"))
    Calculate(firstNumber, secondNumber)


GetNumbers()
