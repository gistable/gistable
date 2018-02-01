# http://en.wikipedia.org/wiki/Extreme_points_of_the_United_States#Westernmost
top = 49.3457868 # north lat
left = -124.7844079 # west long
right = -66.9513812 # east long
bottom =  24.7433195 # south lat

def cull(l):
    c = []
    for (lat, lng) in l:
        if bottom <= lat <= top and left <= lng <= right:
            c.append((lat, lng))
    
