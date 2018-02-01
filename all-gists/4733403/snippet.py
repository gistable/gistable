import re, sys, json

TOKENS = {
    'NUMBER': '[0-9]+', 
    'IDENTIFIER': '[a-zA-Z][a-zA-Z0-9]*', 
    'ADD': '\+', 
    'SUB': '-', 
    'POW': '\^',
    'MUL': '\*', 
    'DIV': '/',
    'LPAREN': '\(',
    'RPAREN': '\)',
    'EOF': '$'
}

class Token:
    EOF = lambda p: Token('EOF', '', p)

    def __init__(self, name, image, position):
        self.name = name
        self.image = image
        self.position = position

class Scanner:
    def __init__(self, expr):
        self.expr = expr
        self.position = 0

    def match(self, name):
        match = re.match('^\s*'+TOKENS[name], self.expr[self.position:])
        return Token(name, match.group(), self.position) if match else None

    def peek(self, *allowed):
        for match in map(self.match, allowed):
            if match: return match

    def next(self, *allowed):
        token = self.peek(*TOKENS)

        if not token:
            raise Exception("Cannot understand expression at position {}: '{}'".format( 
                              self.position, self.expr[self.position:]))

        if token.name not in allowed:
            raise Exception("Unexpected {} at position {}, expected one of: {}".format( 
                              token.name, self.position, ", ".join(allowed)))

        self.position += len(token.image)
        return token
       
    def maybe(self, *allowed):
        if self.peek(*allowed):
            return self.next(*allowed)
        
    def following(self, value, *allowed):
        self.next(*allowed)
        return value
        
    def expect(self, **actions):
        token = self.next(*actions.keys())
        return actions[token.name](token)
        
def evaluate(expr, variables={}):
    tokens = Scanner(expr)
    
    def Binary(higher, **ops):
        e = higher()        
        while tokens.peek(*ops):
            e = ops[tokens.next(*ops).name](e, higher())
        return e
  

    def Add(): return Binary(Mul, ADD=int.__add__, SUB=int.__sub__)
    def Mul(): return Binary(Pow, MUL=int.__mul__, DIV=int.__div__)
    def Pow(): return Binary(Neg, POW=int.__pow__)

    def Neg():
        return -Neg() if tokens.maybe('SUB') else Primary()

    def Primary():
        return tokens.expect(
            NUMBER = lambda x: int(x.image),
            IDENTIFIER = lambda x: variables[x.image],
            LPAREN = lambda x: tokens.following(Add(), 'RPAREN')) 

    return tokens.following(Add(), 'EOF')
    
if __name__ == '__main__':
    print evaluate(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})