'''
  by Adrian Statescu <adrian@thinkphp.ro>
  MIT Style License
'''
def merge(arrA,arrB):
    arrC = []
    i = 0
    j = 0
    n = len(arrA)-1
    m = len(arrB)-1

    while i<=n and j<=m:
          if arrA[i] <= arrB[j]:
            arrC.append(arrA[i])
            i += 1 
          else:
            arrC.append(arrB[j])
            j += 1

    if i<=n:
      for x in range(i,n+1):
          arrC.append(arrA[x])
    elif j<=m:
      for y in range(j,m+1):
          arrC.append(arrB[y])
                    
    return arrC

if __name__ == "__main__":   
    l = ([1,3,5],[2,4,6],[7,8,9,10,11],[22,33,44,88,99]) 
    n = len(l)
    i = 1
    ll = l[0]
    while i<n:
       ll = merge(ll,l[i])
       i +=1     
    print ll 
      