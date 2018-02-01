def main():
    n,k=[int(i) for i in input().split(' ')]
    a=[1]*(n+1)
    for i in range(1,min(k, n+1)):
        a[i]=a[i-1]+a[i-1]
    if k <= n:
        a[k]=sum([a[j] for j in range(k)])
    for i in range(k+1, n+1):
        a[i]=a[i-1]+a[i-1]-a[i-k-1]
    print(str(a[n]))

main()
