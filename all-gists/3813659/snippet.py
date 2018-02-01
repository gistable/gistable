import re

from ply import lex, yacc
from ply.lex import TOKEN
import pyparsing as pp

# First, let's define a pyparsing parser for JSON.
class JSONPyParsing(object):
    # pylint: disable-msg=W0104,E0213

    # JSON Elements ("expressions") are either null, booleans,
    # strings, numbers, objects, or arrays
    null = pp.Keyword('null').setParseAction(pp.replaceWith(None))
    boolean = (
        pp.Keyword('true').setParseAction(pp.replaceWith(True)) |
        pp.Keyword('false').setParseAction(pp.replaceWith(False))
    )

    # A real JSON string has unicode escape sequences and escaped
    # control sequences, but we'll ignore them here.
    string = pp.QuotedString('"', escChar='\\')

    # A number is defined as [+-]?(0|[1-9][0-9]*)([.][0-9]*)?([eE][+-]?[0-9]+)?
    number = pp.Regex(
        r"""[+-]?
            (0 | [1-9][0-9]*)
            (?P<float>
              ([.][0-9]*)?
              ([eE][+-]?[0-9]+)?
            )""",
        flags=re.X
    )

    # A more verbose way to define numbers:
    # plusminus = pp.oneOf('+ -')
    # number = pp.Combine(
    #     pp.Optional(plusminus) +
    #     ('0' | pp.Word('123456789', pp.nums)) +
    #     (pp.Optional(pp.Word('.', pp.nums)) +
    #      pp.Optional(pp.CaselessLiteral('e') +
    #                  pp.Optional(plusminus) +
    #                  pp.Word(pp.nums)))('float')
    # )

    # Define how to process these elements.
    def number_action(tok):
        # pylint: disable-msg=E1101
        if tok.float: return [float(tok[0])]
        return [int(tok[0])]
    
    number.setParseAction(number_action)

    # Objects and Arrays are defined in terms of expr, and expr is
    # defined in terms of objects and arrays. When elements are
    # defined recursively, use Forward() as a placeholder and << to
    # define the value later.
    expr = pp.Forward()

    # Arrays are defined as '[' (expr {',' expr}) ']'
    arr = (
        pp.Suppress('[') +
        pp.Optional(pp.delimitedList(expr)('elements')) +
        pp.Suppress(']')
    )

    # Objects are defined as '{' (string ':' expr {',' string: expr}) '}'
    keyval = string('key') + pp.Suppress(':') + expr('value')
    obj = (
        pp.Suppress('{') +
        pp.Optional(pp.delimitedList(pp.Group(keyval))('elements')) +
        pp.Suppress('}')
    )    

    # Set actions to convert them into the equivalent Python types.    
    def arr_action(tok):
        # pylint: disable-msg=E1101        
        return [list(tok.elements)]

    def obj_action(tok):
        # pylint: disable-msg=E1101        
        return [dict((t.key, t.value) for t in tok.elements)]

    obj.setParseAction(obj_action)
    arr.setParseAction(arr_action)

    # Now that we have defined obj and arr in terms of expr, we can
    # "fill in" the definition of expr.
    expr << (null | boolean | string | number | obj | arr)
    
    # A valid JSON Document has either an object or array at the top level
    json = obj | arr

    @staticmethod
    def loads(json_string):
        return JSONPyParsing.json.parseString(json_string, parseAll=True)[0]

# Now, let's define a PLY parser for JSON.
# PLY requires us to define a 'lexer', which transforms an input
# string into tokens, and a 'parser', which transforms streams of
# tokens into an AST.
    
class JSONPlyLexer(object):

    states = (
        ('str', 'exclusive'),
        ('esc', 'exclusive')
    )
    
    tokens = (
        'INT',
        'FLOAT',
        'NULL',
        'TRUE',
        'FALSE',
        'LBRACE',
        'RBRACE',
        'LBRACKET',
        'RBRACKET',
        'COMMA',
        'COLON',
        'DBLQUOTE',
        'CHAR'
    )

    def __init__(self):
        self.lexer = lex.lex(module=self)

    def __iter__(self):
        return iter(self.lexer)
        
    def token(self):
        return self.lexer.token()

    # Lexing rules as variables are checked in order of longest length.
    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_COMMA = r','
    t_COLON = r':'
    t_TRUE = r'true'
    t_FALSE = r'false'
    t_NULL = r'null'
    
    # Lexing rules in methods are specified using regex docstrings,
    # and checked in the order that they are defined.
    def t_FLOAT(self, t):
        r'(0|[1-9][0-9]*)([.][0-9]*)?([eE][+-]?[0-9]+)?'
        if '.' in t.value or 'e' in t.value:
            t.value = float(t.value)
        else:
            t.type = 'INT'
            t.value = int(t.value)
        return t

    def t_DBLQUOTE(self, t):
        r'"'
        self.lexer.push_state('str')
        return t

    def t_esc_DBLQUOTE(self, t):
        r'"'
        self.lexer.pop_state()
        t.value = u'"'
        t.type = 'CHAR'
        return t
    
    def t_esc_CHAR(self, t):
        'b|n|r|t|f|u[0-9]{4}'
        self.lexer.pop_state()
        t.value = eval('u"\\%s"' % t.value)
        return t

    def t_esc_error(self, t):
        raise SyntaxError(t)

    def t_str_CHAR(self, t):
        r'.'
        if t.value == '\\':
            self.lexer.push_state('esc')
            return None
        elif t.value == '"':
            self.lexer.pop_state()
            t.type = "DBLQUOTE"
            return t
        elif t.value not in ('\b\r\t\f\n'):
            t.value = unicode(t.value)
            return t
        else:
            raise ValueError(t.value + ' not a valid string character')

    def t_str_error(self, t):
        raise SyntaxError(t)
        
    def t_ignore_whitespace(self, t):
        r'\s+'
        pass

    def t_error(self, t):
        raise SyntaxError(t)

    def input(self, data):
        self.lexer.input(data)
    
class JSONPlyParser(object):

    # The Lexer and Parser must share the same set of tokens.
    tokens = JSONPlyLexer.tokens

    def __init__(self):
        self.lexer = JSONPlyLexer()
        self.parser = yacc.yacc(module=self)

    # The first rule specified is the top level rule.
    # Rules are defined in each docstring in BNF.
    # Rules should be left-factored: No two rules
    # should share a prefix longer than 1.
        
    def p_json(self, p):
        '''
        json : obj
             | arr
        '''
        p[0] = p[1]
    
    def p_expr(self, p):
        '''
        expr : NULL
             | TRUE
             | FALSE
             | INT
             | FLOAT
             | string
             | obj
             | arr
        '''
        p[0] = p[1]

    def p_string(self, p):
        '''
        string : DBLQUOTE DBLQUOTE
               | DBLQUOTE chars DBLQUOTE
        '''
        if len(p) == 3:
            p[0] = u''
        else:
            p[0] = p[2]

    def p_chars(self, p):
        '''
        chars : CHAR
              | chars CHAR
        '''
        if len(p) == 1:
            p[0] = u""
        elif len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] + p[2]

    def p_obj(self, p):
        '''
        obj : LBRACE RBRACE
            | LBRACE members RBRACE

        '''
        p[0] = {}
        if len(p) > 3:
            p[0].update(p[2])

    def p_arr(self, p):
        '''
        arr : LBRACKET RBRACKET
            | LBRACKET elements RBRACKET
        '''
        p[0] = []
        if len(p) > 3:
            p[0].extend(p[2])

    def p_members(self, p):
        '''
        members : string COLON expr
                | members COMMA string COLON expr
        '''
        if len(p) == 4:
            p[0] = [(p[1], p[3])]
        else:
            p[0] = p[1]
            p[0].append((p[3], p[5]))

    def p_elements(self, p):
        '''
        elements : expr
                 | elements COMMA expr
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1]
            p[0].append(p[3])

    def p_error(self, p):
        raise SyntaxError(p)
            
    def parse(self, text):
        return self.parser.parse(text, self.lexer)

    instance = None
    
    @staticmethod
    def loads(json_str):
        if JSONPlyParser.instance is None:
            JSONPlyParser.instance = JSONPlyParser()
        return JSONPlyParser.instance.parse(json_str)
