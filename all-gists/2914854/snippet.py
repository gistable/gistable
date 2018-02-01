def is_even(num):
    "Returns true iff num is even."
    
    i = 0
    while i < num:
        i += 2
        
    return i == num
    
def get_even_numbers(a, b):
    "Get all the even numbers between a and b inclusive."
    
    result = []
    
    for i in range(a, b + 1):
        if is_even(i):
            result.append(i)
            
    return result

# Testing
print get_even_numbers(5, 100)
