import sys

def lerp(t):
    r = t * 1.0 + (1-t) * 1.0
    g = t * 0.0 + (1-t) * 1.0
    b = t * 0.0 + (1-t) * 1.0
    r = int(255.0*r)
    g = int(255.0*g)
    b = int(255.0*b)
    return "rgb("+str(r)+","+str(g)+","+str(b)+")"

def color(x, vals):
    if x == -1:
        return "#CCCCFF"
    nth = 0
    for i in range(0, len(vals)):
        #print x," ",vals[i]
        if vals[i] == x:
            nth = i
            #print nth
            break
    p = (1.0*nth)/len(vals)
    #p = (1.0*x)/maxval
    return lerp(p)

def pad(l):
    s = str(l)
    d = 4 - len(s)
    for i in range(0,d):
        s = " "+s
    return s

def parseFragment(lines):
    data = []
    pp = -1#int(sys.argv[2])
    
    for line in lines:
        if "=>" in line:
            continue
        if pp == -1:
            if "." in line:
                pp = line.find(".")+1
            else:
                pp = 10

        value = -1
        pref = line[:pp]
        suf = line[pp:]
        if "." not in pref and pref.strip() != "":
            value = int(pref.replace(",",""))
        data = data + [(value, suf)]

    vals = []
    maxval = 0
    for pt in data:
        if pt[0] == -1:
            continue
        maxval = max(maxval, pt[0])
        vals += [pt[0]]

    vals = sorted(set(vals))
    #print vals

    l = 1
    for pt in data:
        print "<pre style=\"background-color: "+color(pt[0], vals)+";display:block;margin:0;width:100vw\">",
        print pad(l),
        l += 1
        print " | ",
        print pt[1],
        print "</pre>"


if len(sys.argv) < 2:
    print "Usage:"
    print "callgrind_annotate --context=1000 --auto=yes --threshold=100 callgrind.out.[pid] > callgrind.txt"
    print "python "+sys.argv[0]+" callgrind.txt > callgrind.html"
    sys.exit(1)

fname = sys.argv[1]
lines = []

with open(fname) as f:
    lines = f.readlines()

print "<html><head><meta charset=\"UTF-8\"></head><body>"

fragment = []
parsing = False

for line in lines:
    if parsing:
        if "------------------------------------" in line and len(fragment) > 0:
                parsing = False
                parseFragment(fragment[3:])
                fragment = []
        else:
            fragment = fragment + [line]
    else:
        if "-- Auto-annotated source:" in line:
            print "<h1>"+line+"</h1>"
            parsing = True

print "</body>"

