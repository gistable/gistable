'''
Common-prime (in group order!) RSA with low private exponent.
p = 2ga + 1
q = 2gb + 1
N = p * q
phi(N) = 2gab
'''

from sage.all import *


F = PolynomialRing(ZZ, names='x,y')
x, y = F.gens()

if 0:
    print "# RSA generated sample - 512 bits"
    debug = 1

    n   = 'bits: 511(*8 = 4088):' and 6332209924906212950816505180496214422855463382080555526624065510289860012943655551527746445592934358298843747768711404596123307443271433986242907192036903
    lcm = 'bits: 307(*8 = 2456):' and 143204633245102305770892944333114088164113267378582222077214858741657557576780457628982148872
    e   = 'bits: 306(*8 = 2448):' and 102573151860923483482923635426844028877725507002960664276202012941781377721174662183122336581
    d   = 'bits:  81(*8 =  648):' and 2297833573541091530506325
    p   = 'bits: 256(*8 = 2048):' and 96078657335310124036719788604006385717997522720399015824884106923763004145007
    q   = 'bits: 256(*8 = 2048):' and 65906519725885527799387426619815010642569160879093905257080055731449910333129
    k   = 'bits:  81(*8 =  648):' and 1645868759613054159239517
    g   = 'bits: 204(*8 = 1632):' and 22108956188827705981683764894239934965534004098276290804789247
    a   = 'bits:  51(*8 =  408):' and 2172844717650249
    b   = 'bits:  51(*8 =  408):' and 1490493697734812

    N = n - 1

    f = (e*x - 1) * (e*x - 1 + y)

    solx = d
    soly = k * (a + b)
    X = solx + 100
    Y = soly + 100
else:
    print "# Plaid CTF 2017 Quals - Common (Crypto 600) - common prime RSA with small d"
    debug = 0

    TASK_N = n = 58088432169707511884530887899705328460043341752051203523596713643978064163990486003388043207708974302843002172264417411586749486956628013574926573715095249317804208372132481594468281365459316852927039797580064466731086129431102303726096683810636192790138689214881951836298576801818592777778548978736174404573637727968467102304994883348510912250960513170991711142297420921866513951251779528983034404550484931629702384165892697556071097115581299228167852394258387798734409094231193145682416393190929132395057494573898497863918989076392413537702062176268786330410635086565380004463707094857932051066439903977555824218219175469965671350998705376046031482320586719742092257095632485346554447599297796154806971819544073874759609887168714861438380508381072200369356855424637087904990126639040356052220595703217836390163784968964557550834138598331720685971193948909145336792118311346853933919997080542485529346554810899612986872128053464963893904969598870571593590391792680177336466285483108769678524923709955832516312592396932275858180384073997491565078915852990631405792518132787289319255490058314797418779789436482247156880548274241414788581503832731423362447015575598719157544932430682335826661205441977262084135022109705809490179219483
    TASK_E = e = 1296863142627338816011174237898978985407338763709131570002553514972553044428195580769854555546152719732990573444787592853632636242677007643888487629752955065888264014132275294946697123213980215879592216819850992977582758776020797257958443371755687921634978634111557036569863976062810460472490135115734285081745257140890782551910267112228842110620084653440977034007333330590567591507504424149155838966172077983891168269103390479149309815192817914537419492632845858394205854892694802909512194639800529863998537677351955149803841057222279150345376221210193853988829004456607875070080035867353641697190133291884195010172677474092272163240020759433657106746641878734177642792083528380007586872967990567342937466301144028345682953828338178443155
    TASK_ENC_2 = pow(2, TASK_E, TASK_N)

    N = n - 1

    f = (e*x - 1) * (e*x - 1 + y)

    # doubled values from another generated sample
    # [!] the algorithm is quite sensitive to these..
    X = 2**657  # d
    Y = 2**1066 # k (a + b)
    # X = 2**700 <- does not work...

    debug = 0

# info
bits_XY = RR(log(X*Y, 2))
bits_N = RR(log(N, 2))
print "Ratio:", bits_XY, "/", bits_N, "=", bits_XY / bits_N

# polynomial is fine?
if debug:
    assert 0 == f.subs(x=solx, y=soly) % N
    assert 0 != f.subs(x=solx+1, y=soly) % N
    assert 0 != f.subs(x=solx, y=soly+1) % N
assert 0 != f.subs(x=123, y=31337)

# [!] configurable parameters, by hand...
m = 3
my = 2
mxy_x = 1
mxy_y = 1

# generate polynomials for lattice
polys = []
for k in xrange(m + 1):
    for i in xrange(m - k +1):
        p = x**i * f**k * N**(m-k)
        p = p.subs(x=x*X, y=y*Y)
        polys.append( p )

    for i in xrange(my + 1):
        p = y**i * f**k * N**(m-k)
        p = p.subs(x=x*X, y=y*Y)
        polys.append( p )

    for i in xrange(mxy_x + 1):
        for j in xrange(mxy_y + 1):
            p = x**i * y**j * f**k * N**(m-k)
            p = p.subs(x=x*X, y=y*Y)
            polys.append( p )

polys = sorted(set(polys))

# monomials <-> indices
monos = set()
for p in polys:
    for c, mono in p:
        monos.add(mono)

mono_order = sorted(monos)

# make matrix with lattice rows
m = matrix(ZZ, len(polys), len(mono_order))
for yi, p in enumerate(polys):
    for c, mono in p:
        xi = mono_order.index(mono)
        m[yi,xi] = c

print "LLL...", m.nrows(), "x", m.ncols()
m = m.LLL()
print "Done\n"

def topoly(hrow):
    return sum(c*mono/mono.subs(x=X,y=Y) for c, mono in zip(hrow, mono_order)).change_ring(QQ)

# forming polys from coefficients
hs = []
for hrow in m:
    if not hrow:
        continue
    h = topoly(hrow)
    if debug:
        assert h.subs(x=solx,y=soly) % N == 0
        if h.subs(x=solx,y=soly) == 0:
            hs.append(h)
            print "Got poly with good root over ZZ. (%d total)" % len(hs)
    else:
        hs.append(h)

print "Polys", len(hs)


# find two algebraically independent polys with target roots
def find_roots(hs):
    roots = set()
    yy = y.change_ring(QQ)
    assert str(y) == "y"
    itr = 0
    RQQ = PolynomialRing(QQ, names='x')
    # TODO: consider smallest h1, h2 first
    for h1, h2 in Combinations(hs, 2):
        itr += 1
        if itr % 10 == 0:
            print itr, "/", binomial(len(hs), 2)
        res = h1.resultant(h2, yy)
        res = RQQ(res)
        if not res:
            continue
        for r, multiplicity in res.roots():
            r = int(r) % N
            if r and r not in roots:
                roots.add(r)
                yield r

for r in find_roots(hs):
    print "Got root!", r
    if debug:
        if r == solx:
            print "Root matches the solution!"
    elif pow(TASK_ENC_2, r, TASK_N) == 2:
        print "Solution!"
        print "d =", r

        # decrypting flag, basic stuff
        import sys
        sys.path += ["/usr/lib/python2.7/dist-packages/"] # for gmpy
        from rsatool import RSA  # https://github.com/ius/rsatool
        from Crypto.PublicKey import RSA as RSA2
        from Crypto.Cipher import PKCS1_OAEP

        rsa = RSA(n=TASK_N, d=r, e=TASK_E)
        with open("priv.pem", "w") as fk:
            fk.write(rsa.to_pem())
        print "Key written!"

        key = RSA2.construct(map(long, (rsa.n, rsa.e, rsa.d, rsa.p, rsa.q)))
        cipher = PKCS1_OAEP.new(key)
        print `cipher.decrypt(open("flag.enc").read())`

        # 'PCTF{Beh0ld_th3_sm1th_of_C0pper_4nd_7he_var1at3_of_Tri}'

        quit()
