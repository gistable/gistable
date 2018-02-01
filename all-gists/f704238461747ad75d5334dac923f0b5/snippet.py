# Python 3
something = [1,2]

for n in something:
    another = something
    if n < 3:
        another.append(3)

print(another)