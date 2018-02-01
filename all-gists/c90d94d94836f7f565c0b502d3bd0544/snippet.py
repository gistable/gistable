def executeBrainfuck(brainfuckCode):
    valueList = [0]
    listPointer = 0
    programCounter = 0
    programStack = []

    while programCounter < len(brainfuckCode):
        instruction = brainfuckCode[programCounter]

        if instruction == ">": # Increment pointer
            # If list isn't long enough, increase length
            if listPointer + 1 == len(valueList):
                valueList.append(0)
            listPointer += 1

        elif instruction == "<": # Decrement pointer
            listPointer -= 1
            if listPointer < 0: # Pointer out of range
                raise Exception("listPointer is negative")

        elif instruction == "+": # Increment value
            valueList[listPointer] += 1

        elif instruction == "-": # Decrement value
            valueList[listPointer] -= 1

        elif instruction == ".": # Print value
            print(chr(valueList[listPointer]), end='')

        elif instruction == ",": # Input character
            # Ensure a character is inputted
            userInput = ""
            while userInput == "":
                userInput = input()

            # Add first inputted character's ASCII value
            valueList[listPointer] = ord(userInput[0])

        elif instruction == "[": # Start loop
            if valueList[listPointer] == 0:
                unequalBrackets = 1
                # Jump to the end of the loop
                while unequalBrackets > 0:
                    programCounter += 1

                    # Crash if no closing bracket is found
                    if programCounter >= len(brainfuckCode):
                        raise Exception("Unequal brackets in loop. There are " + str(unequalBrackets) + " brackets still open.")

                    if brainfuckCode[programCounter] == "[":
                        unequalBrackets += 1
                    elif brainfuckCode[programCounter] == "]":
                        unequalBrackets -= 1
            else:
                programStack.append(programCounter)

        elif instruction == "]": # End loop
            # Loop must be balanced
            if len(programStack) == 0:
                raise Exception("programStack is empty")

            # If value is 0 continue execution, otherwise loop
            if valueList[listPointer] == 0:
                programStack.pop()
            else:
                programCounter = programStack[-1]

        else: # If invalid character, ignore it
            pass

        programCounter += 1

# Example brainfuck code
brainfuckCode = "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."
executeBrainfuck(brainfuckCode)
