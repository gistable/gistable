def square_sum(n):
    number = str(n);
    i = 1;
    while (i <= len(number)):
        if (len(number) % i == 0):
            start = 0;
            sum = 0;
            while (start + i <= len(number)):
                sum += (int(number[start:(start+i)])) ** 2;
                start += i;
            if (sum == n):
                return True;
        i+=1;
    return False;

print(square_sum(8833));