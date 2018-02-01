xs = [ float(i)/64.0 for i in range(-150, 41) ]
ys = [ float(i)/16.0 for i in range(-25,26) ]
for y in ys: 
    s = ''
    for x in xs:
        z = 0j; i = 0
        while i < 10:
            z = z**2 + x+y*1j
            if abs(z) > 2: 
                break   # Get out of inner loop
            i += 1
        if abs(z) <= 2:
            s += '*'
        else: 
            s += ' '
    print(s + '|')

