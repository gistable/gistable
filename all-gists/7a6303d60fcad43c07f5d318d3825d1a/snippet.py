class globall():
    # print(globals.a,globals.b,globals,c) ; 1,2,3
    s='description'
    t='content.txt'

def string_search(t,s): # Searches the first occurence of the search term.
    if s is None:s=globall.s
    if t is None:t=globall.t
    s=s or globall.s
    t=t or globall.t
    with open(t) as f:
        for n,l in enumerate(f,1):
            if s in l:
                print('Discovered on line number',str(n)+'.')
                break

def string_perform(t,s):
    if s is None:s=globall.s
    if t is None:t=globall.t
    s=s or globall.s
    t=t or globall.t
    with open(t) as f:
        for n,l in enumerate(f,1):
            if s in l:
                return n

string_search(0,0) # "Discovered on line number 7."
string_search(0,'249997999009') # "Discovered on line number 10."
string_perform(0,'249997999009') # Return: 10