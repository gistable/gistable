def water(heights):
    vol = 0
    currVol = 0
    maxWall = 0
    for h in heights:
        if h>=maxWall:
            # closed a puddle
            vol += currVol
            currVol = 0;
            maxWall = h
        else:
            # extend current puddle
            currVol += maxWall-h

    # the remaining puddles
    lastWall = 0
    for h in heights[::-1]:
        if h < maxWall:
            if h < lastWall:
                vol += lastWall-h
            lastWall = max(lastWall, h)
        else:
            break

    return vol


hs = [2,5,1,3,1,2,1,7,7,6]
hs2 =  [2,7,2,7,4,7,1,7,3,7]
hs3 = [2,5,1,3,1,2,1,7,5,6]

print water(hs)
print water(hs2)
print water(hs3)