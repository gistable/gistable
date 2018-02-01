name = input("Give me your name: ")
age = int(input("Give me your age: "))
repeat = int(input("How many times to repeat message? "))

print(repeat * "{name}, you will turn 100 in the year {age}\n".format(name=name, age=2016+(100-age)))