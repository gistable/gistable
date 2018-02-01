(lambda n,s,I:n.classobj('h',(),dict(__init__=(lambda M,S,P,C:M.__dict__.update(
dict(R=(S,P),H=C,O=s.socket()))),C=(lambda M:(M.O.connect(M.R),setattr(M,'D',M.O
.makefile()),setattr(M,'S',(lambda l: M.O.send('%s\r\n'%l))),M.S("NICK hue"),M.S
("USER a b c d :LOL!"),setattr(M,'R',lambda n,m: M.S('PRIVMSG %s :%s'%(n,m))),M.
P())),G = (lambda M,S:S.split(' :',1)[1] if' :'in S else ''),P=(lambda M:next(I.
dropwhile((lambda Lu:((lambda L:((lambda: M.S("PONG :%s"%M.G(L))if L.startswith(
'PING')else(lambda P,G,S:({'001':(lambda: M.S('JOIN %s'%M.H)),'PRIVMSG':(lambda:
M.HC(L[1:].split('!',1),P[2],G[1:].split(),G)if G.startswith('!')else None)}.get
(P[1],lambda: None)())if len(P)>1 else None)(L.split(),M.G(L),M.O))()))(Lu.strip
()),True)[1]),iter(M.D)),None)),HC=(lambda M,(N,H),C,P,L: {'hello':lambda:M.R(C,
"HELLO, %s"%(N)),'hack':lambda:M.R(C, "THE PLANET!!!")}.get(P[0], lambda: None)(
)))))(__import__('new'),__import__('socket'),__import__('itertools'))('irc.wtfu'
'x.net',6667,"#testbot").C()