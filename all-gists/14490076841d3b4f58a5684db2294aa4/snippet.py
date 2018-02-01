def quickSort(L):
        if len(L) < 2:
                return L
        p = L[0]
        i  = 1
        for j in range(i,len(L)):
                if L[j] < p:
                        L[j], L[i] = L[i], L[j]
                        i += 1
        L[0], L[i-1] = L[i-1], L[0]

        left_array = quickSort(L[:i])
        right_array = quickSort(L[i:])

        return  left_array  +  right_array