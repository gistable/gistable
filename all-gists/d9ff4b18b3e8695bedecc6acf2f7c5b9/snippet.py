from collections import deque
# Pull email_data.txt, and join into a big huge string of 1000 random emails.
emails = [x.strip() for x in open('email_data.txt', 'r').readlines() if x.strip()]
emails = ';'.join(emails)
print(emails)


def chunks(data, delimiter=";", width=500):
    pieces = deque(data.split(delimiter))
    s = ""
    while(pieces):
        if len(s + delimiter + pieces[0]) <= width:
            if s:
                s = s + delimiter + pieces.popleft()
            else:
                s = pieces.popleft()  # initially, s will just be an email address.
        else:
            yield s 
            s = ""  # reset 's' so we don't yield it immediately
    if s:  # If we have a last bit left, yield it.
        yield s
        s = ""

if __name__ == "__main__":
    for c in chunks(emails):
        print("{}, {}".format(len(c), c))



