(lambda n,s,I:n.classobj    ('h',(),dict(__init__= (    lambda M,S,P,C:M.__dict__
.update(dict(R=(S,P),H=C    ,A=1<<8,O=s.socket()))),    C=(lambda M:(M.O.connect(
        M.R),1/7,           None,              None,    "sock"
        ,setattr            (M,'D'             ,M.O.    #####
        makefile            ()),1              ,None    ,8192
        ,setattr            (M,'S',(lambda l='':M.O.    send(
        l+'\r\n'            ))),M.S("NICK hue"),M.S(    "USER"
        " a b c"            " d :HE"),setattr(M,'R',    lambda
        n,m:M.S(            'PRIV'  'MSG '              '%s :'
        '%s'%(n,            m))),     M.P()             )),G=(
        lambda M            ,S:S.      split            (' :',
        1)[1] if            ' :'        in S            else''
        or''''''            ),P=(        lambda         M:next
(I.dropwhile((lambda Lu:    ((lambda     L:((lambda:    M.S("PONG :%s"%M.G(L))if
L.startswith('PING'''"")    else(lambda P,G,S:({'001'  :(lambda: M.S ('JOIN %s'%

M.H)),'PRIVMSG':(lambda:M.HC(L[1:].split('!',1),P[2],G[1:].split(),G)if (G and G
    [0]=='!')else None)}.get(P[1], lambda: None)())if len(P) > 1 else None)
        (L.split(),M.G(L),M.O))())) (Lu.strip()),True) [1]), iter(M.D)),
            None)),HC=(lambda M,(N,H),C,P,L: {'hello':lambda:M.R(C,
                "HELLO, %s"%(N)),'hack':lambda:M.R(C, "THE PLA"
                    "NET!!!")}.get(P[0], lambda: None)()))
                        ))(__import__('new'),__import__
                            ('socket'),__import__(
                                'itertools'))(
                                    'irc.'
                                'lulz.net',11+
                            6667-11,"#testbot").C()