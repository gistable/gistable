def peek():
    global string
    return string[0]

def eat(c):
    global string
    if peek() == c:
        string = string[1:]
    else:
        raise RuntimeError

def follow():
    c = peek()
    eat(c)
    return c

def more():
    global string
    return len(string) > 0

def regex():
    t = term()

    if more() and peek() == '|':
        eat('|')
        r = regex()
        print("choice {} {}".format(t, r))
        return "({}|{})".format(t, r)
    else:
        #print("term {}".format(t))
        return t

def term():
    f = ""

    while more() and peek() != ')' and peek() != '|':
        n = factor()
        if f != "":
            print("sequence {} {}".format(f, n))
        f = "{}{}".format(f, n)

    return f

def factor():
    b = base()

    while more() and (peek() == '*' or peek() == '?'):
        p = peek()
        eat(p)
        print("{} {}".format("closure" if p == '*' else "option", b))
        b = "({}){}".format(b, p)

    return b

def base():
    if peek() == '(':
        eat('(')
        r = regex()
        eat(')')
        return r
    else:
        print("base {}".format(peek()))
        return follow()

if __name__ == "__main__":
    string = "(a|b?c)*"
    print(regex())
