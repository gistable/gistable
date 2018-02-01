from __future__ import unicode_literals

from collections import defaultdict
from io import StringIO

from rdflib import URIRef, Literal, Variable

def unroll(triples, vars=None):
    """
    Convert list of tuples specifying triples with repeat subjects or
    subjects and predicates to actual triples.

    A python version of Turtle/SPARQL ; and , syntax.

    >>> unroll( [ (FOAF.Person, [ (RDF.type, RDFS.Class),
                                  (RDFS.label, Literal('Person') ) ] )
    [ ( FOAF.Person, RDF.type, RDFS.Class ), ( FOAF.Person, RDFS.label, Literal('Person') ) ]

    """

    for t in triples:
        if not isinstance(t, (list, tuple)):
            yield t
            continue
        if len(t) == 3: s,p,o = t
        elif len(t) == 2: s,p = t
        else: raise Exception("I cannot unroll %s"%(t,))

        if not isinstance(p, (list, tuple)): p = (p,)

        for p in p:

            if isinstance(p, (list, tuple)) and len(p) == 2:
                p,o = p

            if not isinstance(o, (list, tuple)): o = (o,)

            for o in o:

                if vars:
                    s,p,o = [ vars.get(x,x) for x in ( s,p,o ) ]

                yield (s,p,o)




class Vars(object):
    def __init__(self, *vars):
        self.vars = { v:Variable(v) for v in vars }

    @property
    def all(self):
        return self.vars.values()

    def __getitem__(self, key):
        return self.vars[key]

    def __getattr__(self, key):

        try:
            return object.__getattr__(self, key)

        except AttributeError:
            return self.vars[key]

class Neg(object):
    def __init__(self, f):
        self.f = f

    def n3(self, n3=lambda n: n.n3()):
        return '!%s'%(self.f.n3(n3))

class Function(object):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def n3(self, n3=lambda n: n.n3()):
        return '%s(%s)'%(self.name, ', '.join(n3(a) for a in self.args))

    def __invert__(self):
        return Neg(self)

    def __eq__(self, other):
        return Operators.eq(self, other)

    def __ne__(self, other):
        return Operators.ne(self, other)

    def __lt__(self, other):
        return Operators.lt(self, other)

    def __gt__(self, other):
        return Operators.gt(self, other)

    def __le__(self, other):
        return Operators.le(self, other)

    def __ge__(self, other):
        return Operators.ge(self, other)

class Cast(Function):
    def n3(self, n3=lambda n: n.n3()):
        return '%s(%s)'%(n3(self.name), n3(self.args))


class Aggregator(object):

    def __init__(self, name, arg, proj, **kwargs):
        self.name = name
        self.arg = arg
        self.proj = proj
        self.kwargs = kwargs

    def n3(self, n3=lambda n: n.n3()):

        kw = ''
        if self.kwargs: kw = '; ' + '; '.join( '%s="%s"' % item for item in self.kwargs.items() )


        return '(%(name)s(%(arg)s %(kw)s) AS %(proj)s)'%dict(name=self.name,
                                                          arg=n3(self.arg),
                                                          proj=n3(self.proj),
                                                          kw = kw)



class Operator(object):

    def __init__(self, op, lhs, rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def n3(self, n3=lambda n: n.n3()):
        return '%s %s %s'%(n3(self.lhs), self.op, n3(self.rhs))

def create_function(name):

    def init(self, *args):
        Function.__init__(self, name, args)

    return type(str(name), (Function,), dict(__init__=init))

def create_operator(name, op):

    def init(self, *args):
        Operator.__init__(self, op, *args)

    return type(str(name), (Operator,), dict(__init__=init))


def create_aggregator(name):

    def init(self, *args, **kwargs):
        Aggregator.__init__(self, name, *args, **kwargs)

    return type(str(name), (Aggregator,), dict(__init__=init))




class Functions(object):

    cast = Cast

for f in ( "IRI", "isBLANK", "isLITERAL", "isIRI", "isNUMERIC", "BNODE",
           "ABS", "IF", "RAND", "UUID", "STRUUID", "MD5", "SHA1", "SHA256",
           "SHA384", "SHA512", "COALESCE", "CEIL", "FLOOR", "ROUND", "REGEX",
           "REPLACE", "STRDT", "STRLANG", "CONCAT", "STRSTARTS", "STRENDS",
           "STRBEFORE", "STRAFTER", "CONTAINS", "ENCODE_FOR_URI", "SUBSTR",
           "STRLEN", "STR", "LCASE", "LANGMATCHES", "NOW", "YEAR", "MONTH",
           "DAY", "HOURS", "MINUTES", "SECONDS", "TIMEZONE", "TZ", "UCASE",
           "LANG", "DATATYPE", "sameTerm", "BOUND", "EXISTS", "DESC" ):
    setattr(Functions, f, create_function(f))

class Aggregators(object):
    pass

for a in ( "COUNT", "SUM", "MIN", "MAX", "AVG", "SAMPLE", "GROUP_CONCAT" ):
    setattr(Aggregators, a, create_aggregator(a))


class Operators(object):
    pass

for o in [ ('lt', '<'),
           ('gt', '>'),
           ('le', '<='),
           ('ge', '>='),
           ('eq', '='),
           ('ne', '!='),
           ('mul', '*'),
           ('div', '/'),
           ('add', '+'),
           ('sub', '-'),
           ('_and', '&&'),
           ('_or', '||'),
]:
    setattr(Operators, o[0], create_operator(*o))

class Optional(object):

    def __init__(self, triples):
        self.triples = triples

    def __lt__(self, other):
        if isinstance(other, Optional): return self.triples.__lt__(other)
        return False

class SPARQLGenerator(object):

    def __init__(self, namespace_manager):
        self.namespace_manager = namespace_manager

    def _clear(self):
        self.prefixes = {}

    def _qname(self, node):
        try:
            pfx, uri, local = self.namespace_manager.compute_qname(node, False)
            self.prefixes[pfx] = uri
            return '%s:%s'%(pfx, local)
        except:
            return node.n3()


    def _label(self, node):
        if isinstance(node, Literal):
            return node._literal_n3(
                use_plain=True,
                qname_callback=self._qname)

        if isinstance(node, URIRef):
            return self._qname(node)

        return node.n3()


    def _prefix_string(self):
        return '\n'.join( 'PREFIX %s: <%s>'%(p,uri) for p,uri in self.prefixes.items() )

    def _var_string(self, vars):
        return ' '.join(v.n3() if not isinstance(v, tuple) else '(%s as %s)'%(self._label(v[0]), v[1].n3()) for v in vars)

    def _triples_string(self, triples, indents=1):

        res = StringIO()

        triples = unroll(triples)

        triples = sorted(triples)

        indent = '\t'*indents

        last_s = None
        last_p = None

        for t in triples:
            if isinstance(t, Optional) :
                res.write('\n%sOPTIONAL {\n%s\n%s}'%(indent, self._triples_string(t.triples, indents+1), indent))
                continue
            s,p,o = t
            if not last_s: res.write('%s%s %s %s'%(indent, self._label(s), self._label(p), self._label(o)))
            elif s != last_s and last_s: res.write(' .\n%s%s %s %s'%(indent, self._label(s), self._label(p), self._label(o)))
            elif p != last_p and last_p: res.write(' ;\n%s\t%s %s'%(indent, self._label(p), self._label(o)))
            else: res.write(',\n%s\t\t%s'%(indent, self._label(o)))

            last_s, last_p = s, p

        if last_s: res.write(' .')

        return res.getvalue()


    def construct(self, target, source):
        return "CONSTRUCT { %s } WHERE { %s }"%(self._triples_string(target), self._triples_string(source))

    def select(self, vars, triples, optionals=[], filter=None, orderBy=None, groupBy=None, bind={}):
        self._clear()

        res = "SELECT DISTINCT\n\t%s\nWHERE {\n%s\n" % ( self._var_string(vars), self._triples_string(triples) )

        for o in optionals:
            res += '\tOPTIONAL {\n%s\n\t}\n'%self._triples_string(o, 2)

        if filter:
            res += '\tFILTER ( %s )\n'%filter.n3(self._label)

        for v,expr in bind.items():
            res += '\tBIND ( %s as %s )\n'%( self._label(expr), self._label(v))

        res += '}'

        if groupBy:
            if not isinstance(groupBy, (tuple, list)): groupBy = (groupBy, )
            res += ' GROUP BY %s'%( ' '.join(self._label(g) for g in groupBy))

        if orderBy:
            if not isinstance(orderBy, (tuple, list)): orderBy = (orderBy, )
            res += ' ORDER BY %s'%(' '.join(self._label(o) for o in orderBy))

        return self._prefix_string()+'\n\n'+res


if __name__ == '__main__':
    from rdflib import Graph, RDF, Namespace
    from datetime import datetime

    FOAF = Namespace('http://xmlns.com/foaf/0.1/')

    p = Variable('p')
    name = Variable('name')

    g = Graph()
    g.bind('foaf', FOAF)

    print(SPARQLGenerator(g.namespace_manager).select([p,Functions.isIRI(name)],
                                                      [ (p, [ (RDF.type, FOAF.Person), (FOAF.name, name) ] ) ],
                                                      optional=[ (p, [ ( FOAF.knows, p), ( FOAF.age, Literal(3) ) ] ) ],
                                                      filter=Operators.gt(p,Literal(datetime.now()))
    ))
