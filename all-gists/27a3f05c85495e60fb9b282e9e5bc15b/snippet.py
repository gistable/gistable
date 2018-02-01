import random

n = str(random.randint(1000,9999))
nlist = []
cow = 0
for i in n:
    nlist.append(i)

while cow < 4 and exit !="x":
    x = str(input("Choose a 4 digit number, x to exit: "))
    xlist = []
    cow = 0
    bull = 0
    if x!= "x":
        for i in x:
            xlist.append(i)
        for i in nlist:
            if i in xlist and nlist.index(i) == xlist.index(i):
                cow +=1
            if i in xlist and nlist.index(i) != xlist.index(i):
                bull +=1
        print(cow, "cow(s)", bull, "bull(s)")
    else:
        exit = "x"

print(nlist, xlist)


