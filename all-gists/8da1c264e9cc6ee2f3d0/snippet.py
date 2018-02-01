#!/usr/bin/env python 
# Made by 'Mirko van der Waal'
# Distributed under terms of the MIT license.

from random  import randint
from sys     import argv, exit
import getopt

mews =  [
            # 3
            ['mew', 'maw', 'pur', 'mow', 'prr'],
            # 4
            ['meew', 'maow', 'miow', 'meew', 'meow', 'purr','purs'],
            # 5
            ['miaow''meeew','maaow','meoww','maaaw','purrr','mrawr','mrrrr','prrrr','maoow'],
            # 6
            ['meeeew','miaoww','purrrr','meoaww','meeoww','mrawrr','mewmew','meowrr'],
            # 7
            ['mreeewr','prrrrrr','miaowww','meeewww','meeeeew','mewrawr','mrawrrr','rawrrrr','meewmew']
        ]

class Cat(object):
    def __init__(self,  sentence_length = 7,  
                        paragraph_length = 6, 
                        paragraphs = 3,
                        spread = 0,
                        capitalize=False):

        self.sl = randint(sentence_length - spread, 
                                 sentence_length + spread)
        
        self.pl = randint(paragraph_length - spread, 
                                 paragraph_length + spread)
        self.p = paragraphs
        self.c = capitalize

    def speak(self):
        text = []
        for prg in range(0, self.p):
            paragraph = []
            for sntc in range(0, self.pl):
                sentence = []
                for word in range(0, self.sl):
                    v = mews[randint(0, len(mews) - 1)]
                    sentence.append(v[len(v)-1])
                if self.c: paragraph.append(' '.join(sentence).capitalize())
                else: paragraph.append(' '.join(sentence))
            text.append('. '.join(paragraph))
        return '\n\n\n'.join(text)

SL = 12
PL = 8
P  = 4
S  = 2
C  = False

try:                                                                            
    opts, args = getopt.getopt(argv[1:],                                        
            ':hl:b:p:s:c',                                                          
    ['sentence-length', 'paragraph-length=', 'paragraph=', 'spread=', 'capitalize'])
                                                                                 
except Exception as e:                                                          
    print e, exit(0)  

for o, a in opts:
    if   o in ('-l', '--sentence-length'):  SL = int(a)
    elif o in ('-b', '--paragraph-length'): PL = int(a)
    elif o in ('-p', '--paragraph'):        P  = int(a)
    elif o in ('-s', '--spread'):           S  = int(a)
    elif o in ('-c', '--capitalize'):       C  = True
    elif o in ('-h', '--help'):             
        print """
        -l, --sentence-length
        -b, --paragraph-length
        -p, --paragraph
        -s, --spread
        -c, --capitalize
        -h, --help
        """
        exit(0)

Kitty = Cat(SL, PL, P, S, C)

print (Kitty.speak())