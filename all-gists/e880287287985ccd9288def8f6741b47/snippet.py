from __future__ import unicode_literals
import sys

# We only use unicode in our parser, except for __repr__, which must return str.
if sys.version_info.major == 2:
    repr_str = lambda s: s.encode("utf-8")
    str = unicode
else:
    repr_str = lambda s: s


peg_grammar_src = r"""
#                        Parsing Expression Grammars
# Based on:        A Recognition-Based Syntactic Foundation
#                              - Bryan Ford
#
# Modified slightly to use equals sign, simpler character escapes and fixed
# "-" at end of character class. Added a fixed number of repeats (e.g. {3}).
#
# A skipper is added. ~ A B1 B2 ... will parse the Bs as usual, but skips any
# occurrences of A at any point in the Bs. At most one skipper can be active,
# in nested skippers on the deepest one is active. You can disable a skipper
# in a nested rule by using an empty A, e.g.: ~ () [a-z]*.

# Hierarchical syntax
grammar    = ~ spacing definition+ eof
definition = identifier "=" expression
expression = sequence ("/" sequence)*
sequence   = prefix*
prefix     = ("&" / "!")? suffix
suffix     = primary ("?" / "*" / "+" / repeat)?
repeat     = "{" integer "}"
primary    = identifier !"="
           / "~" prefix sequence
           / "(" expression ")"
           / literal / class / "."

# Lexical syntax
integer     = ~ () [0-9]+
identifier  = ~ () ident_start ident_cont*
ident_start = [a-zA-Z_]
ident_cont  = ident_start / [0-9]
literal     = ~ () (
                ['] (!['] char)* ['] /
                ["] (!["] char)* ["]
              )
class       = ~ () "[" (!"]" range)* "]"
range       = char "-" !"]" char / char
char        = "\\" [nrt'"\[\]\\]
            / "\\x" [0-9a-fA-F]{2}
            / "\\u" [0-9a-fA-F]{4}
            / "\\U" [0-9a-fA-F]{8}
            / !"\\" .
spacing     = (space / comment)*
comment     = "#" (!eol .)* eol
space       = " " / "\t" / eol
eol         = "\r\n" / "\n" / "\r"
eof         = !.
"""


class Val(object):
    """Val represents a value resulting from a grammar expression.

    If v is a Val object, str(v) returns the string as found in the source,
    v.v is the value, v.name is the name if the value resulted from a non-
    terminal.

    As a shorthand, you can index v directly, rather than having to write
    v.v[i] to index lists of results."""

    def __init__(self, v, name=None):
        self.name = name
        self.v = v

    def __str__(self):
        if type(self.v) is str: return self.v
        return "".join(str(v) for v in self.v)

    if sys.version_info.major == 2:
        __unicode__ = __str__
        del __str__

    def __repr__(self):
        return repr_str("{}({!r})".format(type(self).__name__, self.v))

    def __getitem__(self, idx): return self.v[idx]
    def __len__(self): return len(self.v)


class Failure(object):
    def __init__(self, i, expected):
        self.i = i
        self.expected = expected

    def readable_err(self, src):
        line, col = 1, 1
        for idx in range(self.i):
            col += 1
            if src[idx] == "\n":
                line += 1
                col = 1
        msg = "error at {}:{}, expected {}".format(line, col, self.expected)
        if hasattr(self, "name"): msg += " (" + self.name + ")"
        return msg

    def __str__(self):
        msg = "error at {}, expected {}".format(self.i, self.expected)
        if hasattr(self, "name"): msg += " (" + self.name + ")"
        return msg

def isfail(obj): return isinstance(obj, Failure)

class AnyCharVal(Val): pass
class StringVal(Val): pass
class CharClassVal(Val): pass
class OptionalVal(Val): pass
class ZeroOrMoreVal(Val): pass
class OneOrMoreVal(Val): pass
class SequenceVal(Val): pass
class ChoiceVal(Val):
    def __init__(self, v, choice, name=None):
        super(ChoiceVal, self).__init__(v, name)
        self.choice = choice


class Expr(object):
    def __init__(self, data):
        self.data = data

    def parse(self, s):
        m, i = self.match(s, 0, no_skip)
        return m

    def __repr__(self):
        return repr_str("{}({!r})".format(type(self).__name__, self.data))

no_skip = lambda s, i: i
class Skipper(Expr):
    def __init__(self, skip_expr, match_expr):
        self.match_expr = match_expr
        self.skip_expr = skip_expr

    def match(self, s, i, parent_skip):
        i = parent_skip(s, i)
        m, i = self.match_expr.match(s, i, self.skip)
        i = self.skip(s, i)
        return m, i

    def skip(self, s, i):
        while True:
            old_i = i
            i = self.skip_expr.match(s, i, no_skip)[1]
            if i == old_i: break
        return i

    def __repr__(self):
        return repr_str("{}({!r}, {!r})".format(type(self).__name__,
                        self.match_expr, self.skip_expr))

class AnyChar(Expr):
    def __init__(self): pass
    def __repr__(self): return repr_str("AnyChar()")
    def match(self, s, i, skip):
        i = skip(s, i)
        if i >= len(s): return Failure(i, self), i
        return AnyCharVal(s[i]), i + 1

class CharClass(Expr):
    def match(self, s, i, skip):
        i = skip(s, i)
        if i >= len(s) or s[i] not in self.data: return Failure(i, self), i
        return CharClassVal(s[i]), i + 1

class String(Expr):
    def match(self, s, i, skip):
        i = skip(s, i)
        ss = s[i:i+len(self.data)]
        if ss != self.data: return Failure(i, self), i
        return StringVal(ss), i + len(self.data)

class AndPredicate(Expr):
    def match(self, s, i, skip):
        m, _ = self.data.match(s, i, skip)
        return (Failure(i, self) if isfail(m) else None), i

class NotPredicate(Expr):
    def match(self, s, i, skip):
        m, _ = self.data.match(s, i, skip)
        return (Failure(i, self) if not isfail(m) else None), i

class Optional(Expr):
    def match(self, s, i, skip):
        m, i = self.data.match(s, i, skip)
        return OptionalVal([] if isfail(m) else [m]), i

class ZeroOrMore(Expr):
    def match(self, s, i, skip):
        l = []
        while True:
            m, i = self.data.match(s, i, skip)
            if isfail(m): return ZeroOrMoreVal(l), i
            if m is not None: l.append(m)

class OneOrMore(Expr):
    def match(self, s, i, skip):
        l = []
        m, i = self.data.match(s, i, skip)
        if isfail(m): return m, i
        while True:
            if m is not None: l.append(m)
            m, i = self.data.match(s, i, skip)
            if isfail(m): return OneOrMoreVal(l), i

class Sequence(Expr):
    def match(self, s, i, skip):
        orig_i = i
        l = []
        for expr in self.data:
            m, i = expr.match(s, i, skip)
            if isfail(m): return m, orig_i
            if m is not None:
                l.append(m)
        if len(l) > 1:
            return SequenceVal(l), i
        return l[0] if l else None, i

class Choice(Expr):
    def match(self, s, i, skip):
        furthest_fail = None
        for choice, expr in enumerate(self.data):
            m, i = expr.match(s, i, skip)
            if not isfail(m):
                return ChoiceVal(m, choice), i
            if furthest_fail is None or m.i >= furthest_fail.i:
                furthest_fail = m
        return furthest_fail, i

class Nonterminal(Expr):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def match(self, s, i, skip):
        m, i = self.expr.match(s, i, skip)
        if m is not None:
            if not hasattr(m, "name"):
                m.name = self.name
        return m, i

    def __repr__(self):
        return repr_str("Nonterminal({!r}, {!r})".format(self.name, self.expr))



def compile_grammar(grammar):
    m = peg_grammar.parse(grammar)
    if isfail(m): raise RuntimeError(m.readable_err(grammar))

    definitions = m
    identifiers = [str(d[0]) for d in definitions]
    if len(identifiers) > len(set(identifiers)):
        raise RuntimeError("duplicate definition")

    # Forward declaration.
    nts = {ident: Nonterminal(ident, None) for ident in identifiers}
    for d in definitions:
        identifier, expr = str(d[0]), d[2]
        nts[identifier].expr = compile_expr(expr, nts)

    return nts[identifiers[0]]

def compile_expr(expr, nts):
    if len(expr[1]) == 0: return compile_seq(expr[0], nts)
    return Choice([compile_seq(expr[0], nts)] +
                  [compile_seq(s[1], nts) for s in expr[1]])

def compile_seq(seq, nts):
    if len(seq) == 0: return String("")
    if len(seq) == 1: return compile_prefix(seq[0], nts)
    return Sequence([compile_prefix(p, nts) for p in seq])

def compile_prefix(prefix, nts):
    predicate = {"&": AndPredicate,
                 "!": NotPredicate,
                  "": lambda s: s}[str(prefix[0])]
    return predicate(compile_suffix(prefix[1], nts))

def compile_suffix(suffix, nts):
    op = str(suffix[1])
    quantifier = {"?": Optional,
                  "*": ZeroOrMore,
                  "+": OneOrMore,
                  "{": lambda p: Sequence([p] * int(op[1:-1])),
                   "": lambda p: p}[op[:1]]
    return quantifier(compile_primary(suffix[0], nts))

def compile_primary(r, nts):
    if r.choice == 0:
        return nts[str(r)]
    elif r.choice == 1:
        return Skipper(compile_prefix(r[1], nts), compile_seq(r[2], nts))
    elif r.choice == 2:
        return compile_expr(r[1], nts)
    elif r.choice == 3:
        return String("".join(char_to_str(ch) for ch in r[1]))
    elif r.choice == 4:
        return CharClass("".join(map(compile_char_range, r[1])))
    return AnyChar()

def compile_char_range(char_range):
    if char_range.choice == 0:
        start = ord(char_to_str(char_range[0]))
        stop = ord(char_to_str(char_range[2])) + 1
        return "".join(chr(c) for c in range(start, stop))
    elif char_range.choice == 1:
        return char_to_str(char_range.v)

def char_to_str(ch):
    if ch.choice == 0:  # Backslash.
        ch = str(ch[1])
        return {"n": "\n", "r": "\r", "t": "\t"}.get(ch, ch)
    elif ch.choice == 4:  # Literal.
        return str(ch)
    return chr(int(str(ch[1]), 16))  # Unicode escape.


def bootstrap_grammar():
    # Equivalent to peg_grammar_src, but directly expressed using primitives.
    # For correctness this grammar was semi-automatically generated from
    # peg_grammar_src after the first version was hand-written.
    Seq, Not, Opt, Str = Sequence, NotPredicate, Optional, String
    eof         = Not(AnyChar())
    eol         = Choice([Str('\r\n'), Str('\n'), Str('\r')])
    space       = Choice([Str(' '), Str('\t'), eol])
    comment     = Seq([Str('#'), ZeroOrMore(Seq([Not(eol), AnyChar()])), eol])
    spacing     = ZeroOrMore(Choice([space, comment]))
    hexchar     = CharClass('0123456789abcdefABCDEF')
    char        = Choice([Seq([Str('\\'), CharClass('nrt\'"[]\\')]),
                          Seq([Str('\\x'), Seq([hexchar] * 2)]),
                          Seq([Str('\\u'), Seq([hexchar] * 4)]),
                          Seq([Str('\\U'), Seq([hexchar] * 8)]),
                          Seq([Not(Str('\\')), AnyChar()])])
    range_      = Choice([Seq([char, Str('-'), Not(Str(']')), char]), char])
    delim       = (lambda start, inner, stop: Seq([
                       Str(start),
                       ZeroOrMore(Seq([Not(Str(stop)), inner])),
                       Str(stop)]))
    stop_skip   = lambda e: Skipper(Str(''), e)
    class_      = stop_skip(delim("[", range_, "]"))
    literal     = stop_skip(Choice([delim("'", char, "'"), delim('"', char, '"')]))
    ident_start = CharClass('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')
    ident_cont  = Choice([ident_start, CharClass('0123456789')])
    identifier  = stop_skip(Seq([ident_start, ZeroOrMore(ident_cont)]))
    integer     = stop_skip(OneOrMore(CharClass('0123456789')))

    expression      = Nonterminal("expression", None)
    prefix          = Nonterminal("prefix", None)
    sequence        = Nonterminal("sequence", None)
    primary         = Choice([Seq([identifier, Not(Str('='))]),
                              Seq([Str('~'), prefix, sequence]),
                              Seq([Str('('), expression, Str(')')]),
                              literal, class_, Str('.')])
    repeat          = Seq([Str('{'), integer, Str('}')])
    suffix          = Seq([primary,
                           Opt(Choice([Str('?'), Str('*'), Str('+'), repeat]))])
    prefix.expr     = Seq([Opt(Choice([Str('&'), Str('!')])), suffix])
    sequence.expr   = ZeroOrMore(prefix)
    expression.expr = Seq([sequence, ZeroOrMore(Seq([Str('/'), sequence]))])
    definition      = Seq([identifier, Str('='), expression])
    grammar         = Skipper(spacing, Seq([OneOrMore(definition), eof]))

    return grammar

peg_grammar = bootstrap_grammar()


if __name__ == "__main__":
    # Demo, simple calculator.
    grammar = compile_grammar(r"""
    line = ~ spacing expr eof
    expr = factor ([+-] factor)*
    factor = exponent (("//" / [*/%]) exponent)*
    exponent = primary ("**" primary)*
    primary = "(" expr ")" / number / "-" primary
    number = ~ "" &("."? [0-9]) [0-9]* ("." [0-9]*)?
    eof = !.
    spacing = (" " / "\t" / "\r\n" / "\n" / "\r")*
    """)

    def eval_expr(expr):
        r = eval_factor(expr[0])
        for f in expr[1]:
            if str(f[0]) == "+": r += eval_factor(f[1])
            else:                r -= eval_factor(f[1])
        return r

    def eval_factor(factor):
        r = eval_exponent(factor[0])
        for p in factor[1]:
            if str(p[0]) == "*":    r  *= eval_exponent(p[1])
            elif str(p[0]) == "//": r //= eval_exponent(p[1])
            elif str(p[0]) == "/":  r  /= eval_exponent(p[1])
            else:                   r  %= eval_exponent(p[1])
        return r

    def eval_exponent(exponent):
        # Right-to-left associativity.
        exps = reversed([exponent[0]] + [e[1] for e in exponent[1]])
        r = eval_primary(next(exps))
        for e in exps:
            r = eval_primary(e) ** r
        return r

    def eval_primary(primary):
        if primary.choice == 0:
            return eval_expr(primary[1])
        elif primary.choice == 1:
            return [int, float][len(primary[1]) > 0](str(primary))
        else:
            return -eval_primary(primary[1])

    def eval_str(s):
        m = grammar.parse(s)
        if isfail(m):
            raise RuntimeError(m.readable_err(s))
        return eval_expr(m)


    print(eval_str("""  5*3+ 20 - 3 * (3)  """))