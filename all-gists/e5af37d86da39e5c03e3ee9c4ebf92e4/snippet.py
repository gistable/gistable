x = input()
x_a=[i for i in x]
print(x_a)
y = list()

for char in x_a:
    if char.islower()==True:
        z=char.upper()
        y.append(z)
    elif char.isupper()==True:
        z=char.lower()
        y.append(z)
print("".join(y))