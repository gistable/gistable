#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import math
import array
import random
import itertools
import collections

import pyaudio


class MMLStatus:
    """テンポとか音符の長さとかの情報を持つ"""
    def __init__(self, T=120, L=4, O=4, Q=5, V=12):
        self.T = T
        self.L = L
        self.O = O
        self.Q = Q
        self.V = V
        
    def __str__(self):
        return 'T=%d, L=%d, O=%d, Q=%d, V=%d' % (self.T, self.L, self.O, self.Q, self.V)
    
    def change(self, cmd):
        if cmd.cmd == '<':
            if self.O < 7: self.O += 1
        elif cmd.cmd == '>':
            if self.O > 0: self.O -= 1
        elif cmd.cmd == 'L':
            if 1 <= cmd.arg <= 64: self.L = cmd.arg
        elif cmd.cmd == 'V':
            if 0 <= cmd.arg <= 16: self.V = cmd.arg
        elif cmd.cmd == 'T':
            if 30 <= cmd.arg <= 240: self.T = cmd.arg
        elif cmd.cmd == 'O':
            if 0 <= cmd.arg <= 7: self.O = cmd.arg
        elif cmd.cmd == 'Q':
            if 1 <= self.Q <= 8: self.Q = cmd.arg - 1



MMLCommand = collections.namedtuple('MMLCommand', 'cmd acci arg dot')
ADSR = collections.namedtuple('ADSR', 'A D S R')
class MMLPlayer:
    """MMLプレイヤー"""
    ACCI = ( 1.0, 1.0/1.06, 1.06, 1.06 )
    DOT  = ( 1.0, 1.5, 1.75, 1.875 )
    
    def __init__(self, tone, adsr=None):
        self.tone = tone
        self.adsr = adsr
        self.stat = MMLStatus()
        
        
    def fetch_token(self, command):
        buf = []
        for c in command.upper():
            if c in (' ', '¥n'):
                continue
            if c in ('A', 'B', 'C', 'D', 'E', 'F', 'G',
                     'R', 'T', 'L', 'O', 'V', 'Q', '>', '<'):
                if buf:
                    yield ''.join(buf)
                    buf = []
            buf.append(c)
        else:
            if buf: yield ''.join(buf)
    
    
    def conv_token(self, token):
        m = re.search(r'([A-Z<>])([-=+#]?)(¥d*)(¥.*)', token)
        if not m: return
        cmd  = m.group(1).upper()
        acci = '=-+#'.index(m.group(2))
        arg  = int(m.group(3) or 0)
        dot  = len(m.group(4))
        return MMLCommand(cmd=cmd, acci=acci, arg=arg, dot=dot)
    
    
    def conv_freq(self, cmd):
        freq = 0
        if cmd.cmd == 'C':
            freq = 261.63
        elif cmd.cmd == 'D':
            freq = 293.66
        elif cmd.cmd == 'E':
            freq = 329.63
        elif cmd.cmd == 'F':
            freq = 349.23
        elif cmd.cmd == 'G':
            freq = 392.00
        elif cmd.cmd == 'A':
            freq = 440.00
        elif cmd.cmd == 'B':
            freq = 493.88
        elif cmd.cmd == 'R':
            freq = 0
        freq *= 2 ** (self.stat.O - 4) * self.ACCI[cmd.acci]
        return freq
    
    
    def conv_length(self, cmd):
        if 1 <= cmd.arg <= 64:
            return cmd.arg
        else:
            return self.stat.L
        
        
    def calc_tim(self, cmd):
        return (60.0 / self.stat.T) * (4.0 / self.conv_length(cmd)) * self.DOT[cmd.dot]
    
    
    def play(self, command):
        p = pyaudio.PyAudio()
        stream = p.open(rate=44100, channels=1, format=pyaudio.paFloat32, output=True)
        
        buf = (0, 0, 0, 0)
        for i, token in enumerate(self.fetch_token(command)):
            cmd = self.conv_token(token)
            
            if i % 20 == 0:
                sys.stdout.write('¥033[2J¥033[0;0H')
            print cmd, self.stat
            
            if cmd.cmd not in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'R'):
                self.stat.change(cmd)
                continue
            
            freq = self.conv_freq(cmd)
            tim  = self.calc_tim(cmd)
            tim2 = tim * ((self.stat.Q + 1) / 8.0)
            velocity = self.stat.V / 16.0 * 0.1
            
            if cmd.cmd != 'R':
                stream.write(self.tone(buf[0], sec=(buf[1], buf[2]), velocity=velocity, adsr=self.adsr))
                buf = (freq, tim, tim2, velocity)
            else:
                buf = (buf[0], buf[1] + tim, buf[2], velocity)
        else:
            stream.write(self.tone(buf[0], sec=(buf[1], buf[2]), velocity=velocity, adsr=self.adsr))
            
        stream.close()
        p.terminate()
        
        
    def malkov_play(self, command, length=3):
        p = pyaudio.PyAudio()
        stream = p.open(rate=44100, channels=1, format=pyaudio.paFloat32, output=True)
        
        ent = collections.namedtuple('ent', 'freq tim tim2')
        
        entities = [ ]
        for token in self.fetch_token(command):
            cmd = self.conv_token(token)
            if cmd.cmd not in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'R'):
                self.stat.change(cmd)
            else:
                freq = self.conv_freq(cmd)
                tim  = self.calc_tim(cmd)
                tim2 = tim * ((self.stat.Q + 1) / 8.0)
                entities.append(ent(freq, tim, tim2))

        velocity = 0.1
        malkov = dict()
        for i in xrange(length, len(entities)):
            key = tuple(entities[i-length:i])
            val = entities[i]
            malkov.setdefault(key, []).append(val)
            
        total_tim = 0
        key = entities[:length]
        key_insurances = set( tuple(key) )
        while total_tim < 120:
            cands = malkov.get(tuple(key))
            if not cands:
                key = list(random.choice(list(key_insurances)))
                continue
            key_insurances.add(tuple(key))
            e = random.choice(cands)
            key = key[1:] + [ e ]
            stream.write(self.tone(e.freq, sec=(e.tim, e.tim2), velocity=velocity, adsr=self.adsr))
            total_tim += e.tim
            print e, total_tim
            
        stream.close()
        p.terminate()
        



def sine_wave(w, n):
    """サイン派"""
    for i in xrange():
        yield math.sin(float(i % w) / w * PI2)

def sawtooth_wave(w, n):
    """ノコギリ波"""
    for i in xrange(n):
        yield (i % w) / float(w)

def square_wave(w, n):
    """矩形波"""
    hw = w / 2
    for i in xrange(n):
        yield 1.0 if i % w <= hw else 0.0


def tone(freq, sec=1, velocity=.2, rate=44100, adsr=None):
    PI2 = math.pi * 2
    
    if isinstance(sec, (int, float)):
        tim = sec
    else:
        sec, tim = sec
    
    w = rate / freq if freq else 0
    
    def envelope_generator():
        if adsr:
            length = rate * sec
            
            i = 0
            attack  = rate * adsr.A
            for i in xrange(int(min(attack, length))):
                yield i / float(attack)
            
            decay   = rate * adsr.D    
            sustain = adsr.S    
            for i in xrange(i, int(min(decay, length))):
                j = i - attack
                yield 1.0 - ((1.0 - sustain) * j / float(decay))
                
            release_start = rate * tim
            for i in xrange(i, int(min(release_start, length))):
                yield sustain
            
            release = rate * adsr.R
            for i in xrange(i, int(min(release, length))):
                j = i - release_start
                yield sustain * (1.0 - (j / float(release)))
                
            for i in xrange(i, int(length)):
                yield 0.0
                
        else:
            for i in xrange(int(rate * sec)):
                yield 1.0
    
    wgen = square_wave
    def gen():
        if w:
            for i, j in itertools.izip(wgen(w, int(rate * sec)), envelope_generator()):
                yield i * j * velocity
        else:
            for i in xrange(int(rate * sec)):
                yield 0
                
    return array.array('f', gen()).tostring()



mario = """
T195 L8 O5
eerercergrr4>grr4<

crr>grrerrarbrb-arg6<c6g6arfgrercd>br4<
crr>grrerrarbrb-arg6<c6g6arfgrercd>br4<

r4gf+fd+rer>g+a<c>ra<cd
r4gf+fd+rer<crccrr4
>r4gf+fd+rer>g+a<c>ra<cd
r4e-rrdrrcrr4r2

r4gf+fd+rer>g+a<c>ra<cd
r4gf+fd+rer<crccrr4
>r4gf+fd+rer>g+a<c>ra<cd
r4e-rrdrrcrr4r2

ccrcrcdrecr>agrr4
<ccrcrcder1
ccrcrcdrecr>agrr4<

eerercergrr4>grr4<
crr>grrerrarbrb-arg6<c6g6arfgrercd>br4<
crr>grrerrarbrb-arg6<c6g6arfgrercd>br4<

ecr>gr4g+ra<frf>arr4
b6<a6a6a6g6f6ecr>agrr4<
ecr>gr4g+ra<frf>arr4
b6<f6f6f6e6d6crr2.

ecr>gr4g+ra<frf>arr4
b6<a6a6a6g6f6ecr>agrr4<
ecr>gr4g+ra<frf>arr4
b6<f6f6f6e6d6crr2.

ccrcrcdrecr>agrr4
<ccrcrcder1
ccrcrcdrecr>agrr4<

eerercergrr4>grr4<

ecr>gr4g+ra<frf>arr4
b6<a6a6a6g6f6ecr>agrr4<
ecr>gr4g+ra<frf>arr4
b6<f6f6f6e6d6crr2.
"""


invention04 = """
 T80
 O4
 L16
 DEFGAB- C#B-AGFE
 L8
 F A <D >G <C# E
 L16
 DEFGAB- C#B-AGFE
 FDEFGA >b-<agfed
 ecdefg >a<gfedc
 defdef >grrrrr
 <cdecde 
 L8
 >f r b-&
 b- a g
 L16
 <c>b-agfe fg a32g32a32g32&g f
 L8
 f <c c
 L32
 cdcdcdcdcdcd
 cdcdcdcdcdcd
 cdcdcdcdcdcd
 L16
 c>b-agfe <c>def#ga b-agfed b-cdefg

 ab<cdef >g#<fedc>b <c>b<dc>ba g#ag#f#ed cdef#g#a
 d<c>bag#f# ef#g#ab<c >f#<edc>ba g#ab<cde >a<fedc>b
 <ag#f#ea8& ad L32c>b<c>b&b16a16 a8&a16 L16 ab-<c >d8f#8a8 b-gab-<cd
 >e<dc>b-ag a8<fef8  >g8 <e8 r8  defgdb- c#b-agfe f8 d8 >g8&
 L16 g<dc#e>a<c# d>b L32<dc#dc#&c#16d16 L16 dc>b-agf b-c#defg a<d >f8ed d4&d8
"""


# MMLPlayer(tone, adsr=ADSR(0., .4, 0., 0.2)).malkov_play(invention04, length=2)
MMLPlayer(tone, adsr=ADSR(0., .4, 0., 0.2)).play(mario)
