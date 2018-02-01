def fizzbuzz(n):
    for i in np.arange(1, n):
        out = ""
        if i%3 == 0:
            out = out + "fizz"
        if i%5 == 0:
            out = out + "buzz"
        print(i, out)