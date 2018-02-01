list(gen)
# ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

items = list()
try:
    while gen:
        item = next(gen)
        items.append(item)
        if item == '4': break
except StopIteration:
    print "log a message"
    pass