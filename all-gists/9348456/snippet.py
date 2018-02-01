# coding:utf-8
import random

class BBOP:
    def __init__(self, expect, words, fixed):
        self.expect = expect
        self.words = words
        self.fixed = fixed
    
    def random(self):
        s = ''
        r = self.words[:]
        f = self.fixed[:]
        random.shuffle(r)
        for i in range(len(self.words) + len(self.fixed)):
            if f[0][0] == i:
                s += f.pop(0)[1]
            else:
                s += r.pop()
        self.result = s
        return s
    
    def get_string(self):
        r = self.random()
        d = (1 - self.distance() / len(self.expect)) * 100
        return '{0} {1:2.2f}%'.format(r, d)

    def distance(self):
        e = self.expect
        r = self.result
        d = [[0] * (len(r) + 1) for i in range(len(e) + 1)]
        for i in range(len(e)+1):
            d[i][0] = i
        for j in range(len(r)+1):
            d[0][j] = j
        for i in range(1, len(e)+1):
            for j in range(1, len(r)+1):
                cost = 0 if e[i - 1] == r[j - 1] else 1
                d[i][j] = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+cost)
        return float(d[-1][-1])

    @staticmethod
    def parse(str):
        expect = ''
        words = []
        fixed = []
        i = 0
        for s in str.split('/'):
            if s[0]=='{' and s[-1]=='}':
                fixed.append((i, s[1:-1]))
                expect += s[1:-1]
            else:
                words.append(s)
            	expect += s
            i += 1
        return BBOP(expect, words, fixed)

bbop = BBOP.parse('ビ/ビ/{ッ}/ド/レ/{ッ}/ド/{・}/オ/ペ/レ/{ー}/ショ/{ン}')
for i in range(10):
    print bbop.get_string()
