def bin_search(L, a):
    if (len(L) == 1):
        return "NO"

    mid = len(L) // 2
    
    if (a < L[mid]):
        return bin_search(L[:mid], a)
    elif (a > L[mid]):
        return bin_search(L[mid:], a)
    else:
        return "YES"

def main():
    a = int(input('Search for: '))
    L = [1,3,5,7,12,18,22,38]
    print(bin_search(L, a))

main()
