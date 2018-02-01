
i = int(input())
a = [int( input()) for x in range(i)]
listDel = []

def delit(n):
    w = []
    for i in range(1,n // 2 + 1):
        if n % i == 0:
            w.append(i)
    w.append(n)
    return w

def printres(myres):
    for aa in range(len(myres)):
        print(myres[aa], ' ')
    return 1

if i == 1:
    t = printres(delit(a[0]))

else:
    for y in range(i):
        res = delit(a[y])
        listDel.append(res)
    ##    print(*res)
    ob = (list(set(listDel[0]) & set(listDel[1])))
    if i == 2:
        t = printres(ob)
    else:
        for j in range(2,i):
            ob = (list(set(ob) & set(listDel[j])))
        t = printres(ob)