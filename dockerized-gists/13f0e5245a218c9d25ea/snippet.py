def factorial(x):
    running_product=1
    for y in range(1,x+1):
        running_product = running_product*y
        print running_product
    return running_product
    
factorial(4)