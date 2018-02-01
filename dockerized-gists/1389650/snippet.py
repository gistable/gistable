def fibonacci(n):

    result = []
    x, y = 0, 1

    while x < n:
    
        result.append(x)

        x, y = y, y + x

    return result

fibonacci(1000)