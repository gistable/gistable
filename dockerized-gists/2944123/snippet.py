# http://www.linuxhomenetworking.com/forums/showthread.php/1095-Linux-console-Colors-And-Other-Trick-s

def printWarning(input):
    print("\033[31m%s\033[0m" % input)    


def funkyprint(input):
    print("\033[36m%s\033[0m" % input)
