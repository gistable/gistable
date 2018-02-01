import sre_compile
import re


class Scanner:

    def __init__(self, rules, flags=0):
        self.scanner = sre_compile.compile(
            '(%s)' % '|'.join('(%s)' % pattern for pattern in rules),
            flags)
   
    def scan(self, string):
        result = []
        append = result.append
        match = self.scanner.scanner(string).match
        i = 0
        while True:
            m = match()
            if not m:
                break
            j = m.end()
            if i == j:
                break
            action = self.lexicon[m.lastindex-1][1]
            if callable(action):
                self.match = m
                action = action(self, m.group())
            if action is not None:
                append(action)
            i = j
        return result, string[i:]