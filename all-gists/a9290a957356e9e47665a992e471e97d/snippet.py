import sys

def printstr(string):
    sys.stdout.write(string)

def func(level):
    if level == 0:
        return

    printstr("anti-")

    func(level -1)

    if level == 1:
        printstr("people")

    if level % 2 == 0:
        printstr("-gun")
    else:
        printstr("-drone")

func(int(sys.argv[1]))
printstr("s\n")
