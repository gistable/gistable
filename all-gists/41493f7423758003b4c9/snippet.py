def multiply(x1, x2):
        x1, x2 = min(x1, x2), max(x1, x2)
        u = 0
        while x1 >= 1:
            if x1 % 2 or x2 % 2:
                u += x2
            x1 /= 2
            x2 *= 2
        return u