"""fod.py Action Phase Assistant for Fields of Despair https://www.gmtgames.com/p-473-fields-of-despair.aspx"""

import random

print('Welcome to the Action Phase Assistant for GMT Games - Fields of Despair')
print()
print(
    '"One day the great European War will come out of some damned foolish thing in the Balkans." -Otto von Bismark ('
    '1888)')
print()

runagain = 'y'

while runagain == 'y':

    # User inputs
    list1 = []
    list2 = []

    # Determine rolltype
    rolltype = int(input("What type of roll is this? 1=ADR 2=Artillery 3=Infantry "))
    if rolltype not in (1, 2, 3):
        print()
        runagain = input("Invalid input. Would you like to start over? y/n ")
        print()
        if runagain == 'y':
            continue
        else:
            print('Goodbye')
            break

    # Determine fortress for artillery and infantry rolls
    if rolltype in (2, 3):
        fortress = int(input("Does either player have a fortress? 0=None 1=Active 2=Passive "))
        if fortress not in (0, 1, 2):
            print()
            runagain = input("Invalid input. Would you like to start over? y/n ")
            print()
            if runagain == 'y':
                continue
            else:
                print('Goodbye')
                break

    # Determine gas for artillery rolls
    if rolltype == 2:
        gas = int(input("Does either player have poison gas? 0=None 1=Active 2=Passive 3=Both "))
        if gas not in (0, 1, 2, 3):
            print()
            runagain = input("Invalid input. Would you like to start over? y/n ")
            print()
            if runagain == 'y':
                continue
            else:
                print('Goodbye')
                break

    # Determine number of D6
    d1 = int(input("How many D6 required for Active Player? "))
    d2 = int(input("How many D6 required for Passive Player? "))

    # Active Player results
    for i in range(0, d1):
        list1.append(random.randint(1, 6))
    print()
    print('======Active Player results======')
    print()
    print(list1)

    # ADR results
    if rolltype == 1:
        print()
        print('Abort (5):', list1.count(5))
        print('Hit (6):', list1.count(6))

    # Artillery results
    if rolltype == 2 and fortress != 2 and gas not in (1, 3):
        print()
        print('Hit (5):', list1.count(5))
        print('Hit (6):', list1.count(6))
    if rolltype == 2 and fortress == 2 and gas not in (1, 3):
        print()
        print('Hit (6):', list1.count(6))
    if rolltype == 2 and fortress != 2 and gas in (1, 3):
        print()
        print('Gas (4):', list1.count(4))
        print('Hit (5):', list1.count(5))
        print('Hit (6):', list1.count(6))
    if rolltype == 2 and fortress == 2 and gas in (1, 3):
        print()
        print('Gas (4):', list1.count(4))
        print('Hit (6):', list1.count(6))

    # Infantry results
    if rolltype == 3 and fortress != 2:
        print()
        print('Hit (5):', list1.count(5))
        print('Hit (6):', list1.count(6))
    if rolltype == 3 and fortress == 2:
        print()
        print('Hit (6):', list1.count(6))

    # Notes
    print()
    if rolltype in (2, 3) and fortress == 2:
        print(
            'Note: First 6 reduces fortress, then blocks. After blocks destroyed, remaining 6(s) reduce fortress. Not '
            'considered destroyed until end of infantry combat.')
        print()
    if rolltype == 2 and gas in (1, 3):
        print('Note: Poison Gas hits applied to blocks only.')

    # Passive Player results and notes
    for j in range(0, d2):
        list2.append(random.randint(1, 6))
    print()
    print('======Passive Player results======')
    print()
    print(list2)

    # ADR results
    if rolltype == 1:
        print()
        print('Abort (5):', list2.count(5))
        print('Hit (6):', list2.count(6))
        # Calculate net damage
        damage1 = list2.count(6)
        if damage1 > d1:
            damage1 = d1
        damage2 = list1.count(6)
        if damage2 > d2:
            damage2 = d2
        # Calculate net aborts
        aborts = list2.count(5) - list1.count(5)
        if aborts < 0:
            aborts = 0
        # Calculate net reveals
        reveals = d1 - damage1 - aborts
        if reveals < 0:
            reveals = 0
        # Print ADR damage and net block reveals
        print()
        print('===========ADR results===========')
        print()
        print('Active Player takes', damage1, 'damage. Passive Player takes', damage2, 'damage.')
        print('Active Player reveals', reveals, 'opponent block(s).')

    # Artillery results
    if rolltype == 2 and fortress != 1 and gas not in (2, 3):
        print()
        print('Hit (5):', list2.count(5))
        print('Hit (6):', list2.count(6))
    if rolltype == 2 and fortress == 1 and gas not in (2, 3):
        print()
        print('Hit (6):', list2.count(6))
    if rolltype == 2 and fortress != 1 and gas in (2, 3):
        print()
        print('Gas (4):', list2.count(4))
        print('Hit (5):', list2.count(5))
        print('Hit (6):', list2.count(6))
    if rolltype == 2 and fortress == 1 and gas in (2, 3):
        print()
        print('Gas (4):', list2.count(4))
        print('Hit (6):', list2.count(6))

    # Infantry results
    if rolltype == 3 and fortress != 1:
        print()
        print('Hit (5):', list2.count(5))
        print('Hit (6):', list2.count(6))
    if rolltype == 3 and fortress == 1:
        print()
        print('Hit (6):', list2.count(6))

    # Notes
    print()
    if rolltype in (2, 3) and fortress == 1:
        print(
            'Note: First 6 reduces fortress, then blocks. After blocks destroyed, remaining 6(s) reduce fortress. Not '
            'considered destroyed until end of infantry combat.')
        print()
    if rolltype == 2 and gas in (2, 3):
        print('Note: Poison Gas hits applied to blocks only.')

    # Start the whole process over again
    print()
    runagain = input("Would you like to make another roll? y/n ")
    print()
    if runagain != 'y':
        print('Goodbye')
