people = 30
cars = 40
buses = 15

if cars > people:
    print("we should take the cars.")
elif cars < people:
    print("we should not take cars.")
else:
    print("we can't decide.")

if buses > cars:
    print("too many buses.")
elif buses < cars:
    print("maybe we could take the buses.")
else:
    print("we still can't decide.")

if people > buses:
    print("ok, let's take the buses.")
else:
    print("fine, let's stay at home then.")

