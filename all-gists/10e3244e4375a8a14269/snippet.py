#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import signal
from os import system


### MENU ###
# Here are all the elements you can import
# Box elements
Box1 = u"⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
Box2 = u"⠋⠙⠚⠞⠖⠦⠴⠲⠳⠓"
Box3 = u"⠄⠆⠇⠋⠙⠸⠰⠠⠰⠸⠙⠋⠇⠆"
Box4 = u"⠋⠙⠚⠒⠂⠂⠒⠲⠴⠦⠖⠒⠐⠐⠒⠓⠋"
Box5 = u"⠁⠉⠙⠚⠒⠂⠂⠒⠲⠴⠤⠄⠄⠤⠴⠲⠒⠂⠂⠒⠚⠙⠉⠁"
Box6 = u"⠈⠉⠋⠓⠒⠐⠐⠒⠖⠦⠤⠠⠠⠤⠦⠖⠒⠐⠐⠒⠓⠋⠉⠈"
Box7 = u"⠁⠁⠉⠙⠚⠒⠂⠂⠒⠲⠴⠤⠄⠄⠤⠠⠠⠤⠦⠖⠒⠐⠐⠒⠓⠋⠉⠈⠈"
Box8 = u"⠁⠂⠄⡀⢀⠠⠐⠈"
Box9 = u"☐☑☐☒"
Box10 = u"¨‧⁘⸪⁙⁝⁛⁚꞉⸭⸫⸬⁖"

# Flags
Flag1 = u"⚑⚐"
Flag2 = u"✓✔"
Flag3 = u"✓✔⎷⍻"
Flag4 = u"✖✗✘✕☓"

# Hands
Hand1 = u"☚☜☝☞☛☟"
Hand2 = u"☚☝☛☟"
Hand3 = u"☜☝☞☟"

# Stars
Star1 = u"★☆"
Star2 = u"✦✧✩✬✭✮✯✰"
Star3 = u"✪✫"
Star4 = u"✦✧✩✪✫✬✭✮✯✰"

# Waving
Wave1 = u"∼≈≅≈"
Wave2 = u"≈≅"
Wave3 = u"∼≈≅"

# Tools
Tool1 = u"☎☏"
Tool2 = u"✆☎☏"
Tool3 = u"☂☔"
Tool4 = u"⌦⌧⌫"
Tool5 = u"✎✏✐"
Tool6 = u"✁✂✃✄"

# Flle elements uploading,sync
File1 = u"⎗⎘⎙"
Sync1 = u"♺♳♴♵♶♷♸♹"
Sync2 = u"♻♲♽♼"

# Poker elements
Dice1 = u"⚀⚁⚂⚃⚄⚅"
Card1 = u"♤♠♣♧♡♥♦♢"
Card2 = u"♤♠"
Card3 = u"♣♧"
Card4 = u"♡♥"
Card5 = u"♦♢"

# Downloading elements
Down1 = u"․‥…"
Down2 = u"⁃‐‑‒–⎯—―"

# Spin element
Spin1 = u"|/-\\"
Spin2 = u"┤┘┴└├┌┬┐"
Spin3 = u"╫╪"
Spin4 = u"∩⊂∪⊃"
Spin5 = u"∩⊂⊆∪⊃⊇"
Spin6 = u"☢☮"
Spin7 = u"↳↰"
Spin8 = u"↱↴↲"
Spin9 = u"↯↳↰"
Spin10 = u"↯↲↱↴"
Spin11 = u"↷↻"
Spin12 = u"↺↶"
Spin13 = u"⟲↺"
Spin14 = u"⟳↻"
Spin14 = u"◜◝◞◟◠◡"
Spin15 = u"╰╮╭╯"
Spin16 = u"✇☣☢"
Xspin1 = u"ᓂ—ᓄ—"
Xspin2 = u"ᓇ—ᓀ—"
Yspin1 = u"d|b|"
Yspin2 = u"q|p|"
Zspin1 = u"dᓇpᓀ"
Zspin2 = u"bᓂqᓄ"

# Arrow element
Arrow1  = u"←↑→↓"
Arrow2  = u'←↖↑↗→↘↓↙'
Arrow3  = u"►▲◄▼"
Arrow4  = u"►△◄▽"
Arrow5  = u"⏪⏫⏩⏬"
Arrow6  = u"⇐⇑⇒⇓"
Arrow7  = u"⬎⬏⬐⬑"
Arrow8  = u"⬀⬂⬃⬁"
Arrow9  = u"⬅⬉⬆⬈➡⬊⬇⬋"
Arrow10 = u"⬌⬉⬍⬈⬌⬌⬊⬍⬋"
Arrow11 = u"⇦⇨⇩⇪⇧"
Arrow12 = u"⇠⇡⇢⇣"
Arrow13 = u"⤣⤥"
Arrow14 = u"⤡⤢"
Arrow15 = u"⤣⤥⤡⤤⤦⤢"
Arrow16 = u"⤣⤥⤤⤦"
Arrow17 = u"⤧⤨⤩⤪"
Arrow18 = u"⤧⤯⤨⤩⤰⤪"
Arrow19 = u"⟵⟸⟽⤊⟰⟾⟹⟶⟹⟾⤋⟱⟽⟸⟵"
Arrow20 = u"➪➭➫➯➬➱➮➯"
Arrow21 = u"➳➴➵➶➷➸➹➺➻➼➽"
Arrow22 = u"⚡⌁☇☈"

# Blocks
Block1 = u"▖▘▝▗"
Block2 = u"▉▊▋▌▍▎▏▎▍▌▋▊▉"
Block3 = u"▁▃▄▅▆▇█▇▆▅▄▃▁"
Block4 = u"▌▄▐▀"
Block5 = u"■□▪▫"
Block6 = u"◩◪"
Block7 = u"⎺⎻⎼⎽"
Block8 = u"⌆⌅⌤⌃"

# Chess
Chess1 = u"♚♔♛♕♜♖♝♗♞♘♟♙"
Chess2 = u"♚♔"
Chess3 = u"♛♕"
Chess4 = u"♜♖"
Chess5 = u"♝♗"
Chess6 = u"♞♘"
Chess6 = u"♟♙"
Chess7 = u"♚♛♜♖♝♞♟"
Chess8 = u"♔♕♖♗♘♙"

# Clocks
Clock1 = u"◐◓◑◒"
Clock2 = u"◰◳◲◱"
Clock3 = u"◴◷◶◵"
Clock4 = u"◡◡⊙⊙◠◠"

# Music
Music1 = u"♩♫♪♬"
Music2 = u"♩♫♪♬♭♮♯🎼"

# Weird
Weird1 = u". o O @ *"
Weird2 = u".oO@*"

# Alphabets
Alphbt1 = u"ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ"
Alphbt2 = u"⒜⒝⒞⒟⒠⒡⒢⒣⒤⒥⒦⒧⒨⒩⒪⒫⒬⒭⒮⒯⒰⒱⒲⒳⒴⒵"

# Number elements
Number1 = u"0123456789"
Number2 = u"⓵⓶⓷⓸⓹⓺⓻⓼⓽⓾"
Number3 = u"⓪①②③④⑤⑥⑦⑧⑨⑩" #has 0
Number4 = u"➀➁➂➃➄➅➆➇➈➉⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
Number5 = u"❶❷❸❹❺❻❼❽❾❿➊➋➌➍➎➏➐➑➒➓⓫⓬⓭⓮⓯⓰⓱⓲⓳⓴"
Number6 = u"⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇"
Number7 = u"¹²³↉½⅓¼⅕⅙⅐⅛⅑⅒⅔⅖¾⅗⅜⅘⅚⅝⅞"

# Trigram
Trigrm1 = u"☰☱☲☳☴☵☶☷"
Trigrm2 = u"☰☱☳☷☴☶☳☱"
Trigrm3 = u"≐≒≑≓≕≑≔"

# Smiley :)
Simley1 = u"⍣⍤⍥⍨⍩"
Simley2 = u"⍤⍥"
Simley3 = u"☺☻☯"
Simley4 = u"⚇⚆⚈⚉"

# Snowflake and sparkle
Snoflk1 = u"❃❅❆"
Sprkle1 = u"❇❈❉❊❋"

# Flowers
Flower1 = u"✲✱✳✴✵✶✷✸✹✺"
Flower2 = u"✻✼✽✾❀✿❁❃❇❈❉❊❋⁕"
Flower3 = u"✢✣✤✥"

# Gender
Gender1 = u"♂⚣⚩♀☿⚢⚤⚦⚧⚨♁"

# Extras
Dollar1 = u"$S"
Vector1 = u"⊕⊗"
Medicine1 = u"☤⚚"
Religion1 = u"✙✚✜✛♰♱✞✟"

Earth1 = u"🌍🌎🌏"
Dot1 = u"·•●"
# You can always add more!
### MENU ###
### END  ###


Default = Box1

a = """
╔════╤╤╤╤════╗
║    ││││    ║
║    ││││    ║
║    OOOO    ║
"""
b = """
╔════╤╤╤╤════╗
║   / │││    ║
║  O  │││    ║
║     OOO    ║
"""
c = """
╔════╤╤╤╤════╗
║    │││ \   ║
║    │││  O  ║
║    OOO     ║
"""
Ultimate1 = [a, b, a, c]

a = """
       __       __
       ) \     / (
      )_  \_V_/  _(
        )__   __(
           `-'
"""

b = """
     ____       ____
     )   \     /   (
      )_  \_V_/  _(
        )__   __(
           `-'
"""

c = """

 _..__.          .__.._
.^"-.._'-(\oVo/)-' _..-"^.
       '-.'    '.-'
          `-..-'
"""
Ultimate2 = [a, b, c, c, b]





CLS = "\033c"
HIDE_CURSOR = '\x1b[?25l'
SHOW_CURSOR = '\x1b[?25h'


class CursorOFF(object):

    """
    Use it for hiding cursor.
    Usage:

    with CursorOFF():
        # do something
        # this part output will have no cursor
        pass
    """

    def __enter__(self):
        system('setterm -cursor off')
        import signal
        import sys

        def handler(signum, frame):
            print SHOW_CURSOR
            sys.exit()
        # signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTSTP, handler)

    def __exit__(self, *args):
        system('setterm -cursor on')

# Decorator
# def cursoroff(f):
#     def wrapped(*args,**kwargs):
#         with CursorOFF():
#             return f(*args,**kwargs)
#     return wrapped

def counter(f):
    """
    Counter Decorator for the next method in Spin object.
    """
    def wrapped(*args, **kwargs):
        wrapped.calls += 1
        return f(*args, **kwargs)
    wrapped.calls = 0
    return wrapped

def worker(sp, message, flag=False):
    """
    Output the spinner without jumping to next line.
    """
    sys.stdout.write(u"\r{0}   {1}".format(sp, message))
    sys.stdout.flush()
    if flag:
        sys.stdout.write(HIDE_CURSOR)


class Spin(object):

    """
    Spinner object in a loop:
    Usage:
    - Next::
    from py-spin import Spin
    import time
    s = Spin()
    for _ in range(50):
        s.next()
        time.sleep(0.1)
    """

    def __init__(self, spinner=Default, message=""):
        self.spinner = spinner
        self.message = message
        # self.cursor = cursor #working on currently

    @counter
    def next(self):
        length = len(self.spinner)
        message = self.message
        # cursor = self.cursor

        # cycle using counter wrapper
        calls = self.next.calls
        i = calls % length
        sp = self.spinner[i]  # spin point
        if type(self.spinner) == list:
            print CLS
            print sp
            print message
        else:
            worker(sp, message)

    @counter
    def Next(self):
        """
        cycles the array
        """
        try:
            self.spinner = self.spinner.decode('utf-8')
        except:
            pass
        length = len(self.spinner)
        calls = self.Next.calls
        i = calls % length
        sp = self.spinner[i]  # spin point
        return sp

    @property
    def all(self):
        ll = globals().keys()
        sll = set(ll)
        removegb ={'signal','SHOW_CURSOR','__all__',
        '__builtins__','__name__','CursorOFF','__doc__',
        'worker','c','__package__','HIDE_CURSOR','sys',
        'a','CLS','system','counter','b','__file__','Spin',}
        ll = sll - removegb
        ll = sorted(list(ll))
        for i in ll:
            if type(globals()[i]) == list:
                print i
                for _ in globals()[i]:
                    print _
            else:
                a = "%s = u'%s'"
                print a%(i,globals()[i])
        return "Add one if you like!"



###############################################
###############################################
################   Example  ###################
###############################################
###############################################

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal
from os import system
import time

# Two types
#
# 1. Spin(<name of element>,<message you wanna give>)
a = Spin(Spin8,"Downloading...")
for i in range(25):
    a.next()
    time.sleep(0.2)

a = Spin(Block4,"Maze Runner...")
for i in range(25):
    a.next()
    time.sleep(0.3)

a = Spin(Clock3,"Clock Ticks...")
for i in range(25):
    a.next()
    time.sleep(0.1)

a = Spin(Number5,"Number game...")
for i in range(25):
    a.next()
    time.sleep(0.1)

# 2. You can hide the cursor too...
with CursorOFF():
    a = Spin(Clock3,"CursorOFF ...")
    for i in range(25):
      a.next()
      time.sleep(0.3)

