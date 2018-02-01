"""
NPR CHALLENGE #1
Week of 10/23/16
(c) 2016 Mark Nash
"""
#Setup
#Random
#Number to go up to
goUpTo = 40
#Numbers in equation
numbersInEquation = [5,4,3,2,1]
#Found numbers
foundNumbers = []
#Not found numbers
notFoundNumbers = []
#Loops
#Go -> all options for each
i = 0
workingNum = 5
while i < 4:
    #each opp type
    if i == 0:
        workingNum += 4
    if i == 1:
        workingNum -= 4
    if i == 2:
        workingNum *= 4
    if i == 3:
        workingNum /= 4
    j = 0
    while j < 4:
        #each opp type
        if i == 0:
            workingNum += 4
        if i == 1:
            workingNum -= 4
        if i == 2:
            workingNum *= 4
        if i == 3:
            workingNum /= 4
        k = 0
        while k < 4:
            #each opp type
            if i == 0:
                workingNum += 1
            if i == 1:
                workingNum -= 1
            if i == 2:
                workingNum *= 1
            if i == 3:
                workingNum /= 1
            l = 0
            while l < 4:
                #each opp type
                if i == 0:
                    workingNum += 1
                if i == 1:
                    workingNum -= 1
                if i == 2:
                    workingNum *= 1
                if i == 3:
                    workingNum /= 1
                l +=1
                #append list after check working num vs upto#
                if workingNum <= goUpTo and workingNum >= (goUpTo * -1):
                    foundNumbers.append(workingNum)
            k += 1
        j += 1
    i += 1
#get uniques
uniqueFoundNumbers = []
m = 0
while m < len(foundNumbers):
    #check if in
    if foundNumbers[m] not in uniqueFoundNumbers:
        uniqueFoundNumbers.append(foundNumbers[m])
    m += 1
#output
print(uniqueFoundNumbers[0:(len(uniqueFoundNumbers)+1)])

"""
ANSWER:
[15, 16, 17, 18, 20, 21, 22, 23, 25, 26, 27, 28, 30, 31, 32, 33, 39, 40, 37, 36, 35, 34, 29, 13, 12, 11, 10, 8, 7, 6, 5]
"""