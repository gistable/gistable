"""
exp ::= term  | exp + term | exp - term
term ::= factor | factor * term | factor / term
factor ::= number | ( exp )
"""

class Calculator():
    def __init__(self, tokens):
        self._tokens = tokens
        self._current = tokens[0]
    
    def exp(self):
        result = self.term()
        while self._current in ('+', '-'):
            if self._current == '+':
                self.next()
                result += self.term()
            if self._current == '-':
                self.next()
                result -= self.term()
        return result

    def factor(self):
        result = None
        if self._current[0].isdigit() or self._current[-1].isdigit():
            result = float(self._current)
            self.next()
        elif self._current is '(':
            self.next()
            result = self.exp()
            self.next()
        return result

    def next(self): 
        self._tokens = self._tokens[1:]
        self._current = self._tokens[0] if len(self._tokens) > 0 else None

    def term(self):
        result = self.factor()
        while self._current in ('*', '/'):
            if self._current == '*':
                self.next()
                result *= self.term()
            if self._current == '/':
                self.next()
                result /= self.term()
        return result

if __name__ == '__main__':
    while True:
        lst = list(raw_input('> ').replace(' ', ''))
        tokens = []
        for i in range(len(lst)):
            if lst[i].isdigit() and i > 0 and  (tokens[-1].isdigit() or tokens[-1][-1] is '.'):
                tokens[-1] += lst[i]          
            elif lst[i] is '.' and i > 0 and tokens[-1].isdigit():
                tokens[-1] += lst[i]
            else:
                tokens.append(lst[i])
        print Calculator(tokens).exp() 
