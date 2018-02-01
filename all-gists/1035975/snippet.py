import ast
from cStringIO import StringIO
import sys

INFSTR = '1e308'

def interleave(inter, f, seq):
  seq = iter(seq)
  try:
    f(next(seq))
  except StopIteration:
    pass
  else:
    for x in seq:
      inter()
      f(x)

class PythonToPhp:
  def __init__(self, source, indent = 0):
    tree = ast.parse(source)
    self.code = StringIO()
    self.tabstop = 2
    self._indent = indent

    self.dispatch(tree)

  def get_code(self):
    return self.code.getvalue()

  def fill(self, text = ''):
    self.code.write('\n%s%s' % (' ' * self.tabstop * self._indent, text))

  def write(self, text):
    self.code.write(text)

  def enter(self):
    self.code.write(' {')
    self._indent += 1

  def leave(self):
    self._indent -= 1
    self.fill('}')

  def error(self, msg):
    print msg
    sys.exit()

  def dispatch(self, tree):
    if isinstance(tree, list):
      for t in tree:
        self.dispatch(t)
      return
    meth = getattr(self, '_%s' % tree.__class__.__name__)
    return meth(tree)

  ########## Transform Methods ##########

  def _Module(self, tree):
    for stmt in tree.body:
      self.dispatch(stmt)

  ### Statement ###

  def _Expr(self, tree):
    self.fill()
    self.dispatch(tree.value)
    self.write(';')

  def _Import(self, t):
    self.error('import not supported')

  def _ImportFrom(self, t):
    self.error('import not supported')

  def _Assign(self, t):
    self.fill()
    for target in t.targets:
      if isinstance(target, ast.Tuple):
        self._lvalue_tuple(target)
      else:
        self.dispatch(target)
      self.write(' = ')
    self.dispatch(t.value)
    self.write(';')

  def _AugAssign(self, t):
    self.fill()
    self.dispatch(t.target)
    name = t.op.__class__.__name__
    if name == 'Pow':
      self.write(' = pow(')
      self.dispatch(t.target)
      self.write(', ')
      self.dispatch(t.value)
      self.write(');')
    elif name == 'FloorDiv':
      self.write(' = floor(')
      self.dispatch(t.target)
      self.write(' / ')
      self.dispatch(t.value)
      self.write(');')
    else:
      self.write(' %s= ' % self.binop[t.op.__class__.__name__])
      self.dispatch(t.value)
      self.write(';')

  def _Return(self, t):
    self.fill('return')
    if t.value:
      self.write(' ')
      self.dispatch(t.value)
    self.write(';')

  def _Pass(self, t):
    self.fill(';')

  def _Break(self, t):
    self.fill('break;')

  def _Continue(self, t):
    self.fill('continue;')

  def _Delete(self, t):
    for target in t.targets:
      self.fill('unset(')
      self.dispatch(target)
      self.write(');')

  def _Assert(self, t):
    self.fill('assert(')
    self.dispatch(t.test)
    self.write(');')

  def _Exec(self, t):
    self.fill('eval(')
    self.dispatch(t.body)
    self.write(');')

  def _Print(self, t):
    self.fill('echo ')
    sep = ''
    for e in t.values:
      self.write(sep)
      self.dispatch(e)
      sep = ', '
    if t.nl:
      self.write(sep)
      self.write("'<br />'")
    self.write(';')

  def _Global(self, t):
    self.fill('global ')
    interleave(lambda: self.write(', '), self.write, t.names)
    self.write(';')

  def _Yield(self, t):
    self.error('yield not supported')

  def _Raise(self, t):
    self.error('Exceptions not supported')

  def _TryExcept(self, t):
    self.error('Exceptions not supported')

  def _TryFinally(self, t):
    self.error('Exceptions not supported')

  def _ExceptHandler(self, t):
    self.error('Exceptions not supported')

  def _ClassDef(self, t):
    self.error('Class not supported')

  def _FunctionDef(self, t):
    self.fill('function ' + t.name + '(')
    self.dispatch(t.args)
    self.write(')')
    self.enter()
    self.dispatch(t.body)
    self.leave()

  def _For(self, t):
    self.fill('foreach (')
    self.dispatch(t.iter)
    self.write(' as ')
    self.dispatch(t.target)
    self.write(')')
    self.enter()
    self.dispatch(t.body)
    self.leave()
    if t.orelse:
      self.error('else clause for for statement not supported')

  def _If(self, t):
    self.fill("if (")
    self.dispatch(t.test)
    self.write(')')
    self.enter()
    self.dispatch(t.body)
    self.leave()
    # collapse nested ifs into equivalent elifs.
    while (t.orelse and len(t.orelse) == 1 and
           isinstance(t.orelse[0], ast.If)):
      t = t.orelse[0]
      self.fill("elseif (")
      self.dispatch(t.test)
      self.write(')')
      self.enter()
      self.dispatch(t.body)
      self.leave()
    # final else
    if t.orelse:
      self.fill("else")
      self.enter()
      self.dispatch(t.orelse)
      self.leave()

  def _While(self, t):
    self.fill("while (")
    self.dispatch(t.test)
    self.write(')')
    self.enter()
    self.dispatch(t.body)
    self.leave()
    if t.orelse:
      self.error('else clause for while statement not supported')

  def _With(self, t):
    self.error('with statement not supported')

  ### Expression ###

  def _Str(self, t):
    self.write(repr(t.s))

  def _Name(self, t):
    if t.id == 'True':
      self.write('true')
    elif t.id == 'False':
      self.write('false')
    elif t.id == 'None':
      self.write('null')
    else:
      self.write('$%s' % t.id)

  def _Repr(self, t):
    self.write('var_export(')
    self.dispatch(t.value)
    self.write(", true)")

  def _Num(self, t):
    repr_n = repr(t.n)
    if repr_n.startswith('-'):
      self.write('(')
    self.write(repr_n.replace('inf', INFSTR))
    if repr_n.startswith('-'):
      self.write(')')

  def _List(self, t):
    self.write('array(')
    interleave(lambda: self.write(", "), self.dispatch, t.elts)
    self.write(')')

  def _ListComp(self, t):
    if len(t.generators) > 1:
      self.error('multiple generators in comprehension not supported')
    generator = t.generators.pop()
    self._comprehension(generator, 'left')
    self.dispatch(t.elt)
    self._comprehension(generator, 'right')

  def _comprehension(self, t, part = 'left'):
    if part == 'left':
      if t.ifs:
        self.write('array_filter(array_map(function(')
      else:
        self.write('array_map(function(')
      self.dispatch(t.target)
      self.write(') { return ')
    elif part == 'right':
      self.write('; }, ')
      self.dispatch(t.iter)
      if t.ifs:
        self.write('), function(')
        self.dispatch(t.target)
        self.write(') { return ')
        for if_clause in t.ifs:
          self.dispatch(if_clause)
        self.write('; })')
      else:
        self.write(')')

  def _GeneratorExp(self, t):
    if len(t.generators) > 1:
      self.error('multiple generators in comprehension not supported')
    generator = t.generators.pop()
    self._comprehension(generator, 'left')
    self.dispatch(t.elt)
    self._comprehension(generator, 'right')

  def _SetComp(self, t):
    if len(t.generators) > 1:
      self.error('multiple generators in comprehension not supported')
    self.write('array_unique(')
    generator = t.generators.pop()
    self._comprehension(generator, 'left')
    self.dispatch(t.elt)
    self._comprehension(generator, 'right')
    self.write(')')

  def _DictComp(self, t):
    self.error('dict comprehension not supported')

  def _IfExp(self, t):
    self.write("((")
    self.dispatch(t.test)
    self.write(') ? (')
    self.dispatch(t.body)
    self.write(') : (')
    self.dispatch(t.orelse)
    self.write('))')

  def _Set(self, t):
    assert(t.elts) # should be at least one element
    self.write('array_unique(array(')
    interleave(lambda: self.write(", "), self.dispatch, t.elts)
    self.write('))')

  def _Dict(self, t):
    self.write('array(')
    def write_pair(pair):
      k, v = pair
      self.dispatch(k)
      self.write(' => ')
      self.dispatch(v)
    interleave(lambda: self.write(', '), write_pair, zip(t.keys, t.values))
    self.write(')')

  def _Tuple(self, t):
    self.write('array(')
    interleave(lambda: self.write(", "), self.dispatch, t.elts)
    self.write(')')

  def _lvalue_tuple(self, t):
    self.write('list(')
    interleave(lambda: self.write(", "), self.dispatch, t.elts)
    self.write(')')

  unop = {"Invert":"~", "Not": "!", "UAdd":"+", "USub":"-"}
  def _UnaryOp(self, t):
    self.write("(")
    self.write(self.unop[t.op.__class__.__name__])
    self.write(" ")
    if isinstance(t.op, ast.USub) and isinstance(t.operand, ast.Num):
      self.write("(")
      self.dispatch(t.operand)
      self.write(")")
    else:
      self.dispatch(t.operand)
    self.write(")")

  binop = { 
    "Add":"+",
    "Sub":"-",
    "Mult":"*",
    "Div":"/",
    "Mod":"%",
    "LShift":"<<",
    "RShift":">>",
    "BitOr":"|",
    "BitXor":"^",
    "BitAnd":"&",
  }
  def _BinOp(self, t):
    name = t.op.__class__.__name__
    if name == 'Pow':
      self.write("(pow(")
      self.dispatch(t.left)
      self.write(', ')
      self.dispatch(t.right)
      self.write('))')
    elif name == 'FloorDiv':
      self.write('(floor(')
      self.dispatch(t.left)
      self.write(' / ')
      self.dispatch(t.right)
      self.write('))')
    elif name == 'Mod' and isinstance(t.left, ast.Str): 
      self.write('sprintf(')
      self.dispatch(t.left)
      self.write(', ')
      if isinstance(t.right, ast.Str):
        self.dispatch(t.right)
      elif isinstance(t.right, ast.Tuple):
        interleave(lambda: self.write(", "), self.dispatch, t.right.elts)
      else:
        self.error('impossible string substript error')
      self.write(')')
    else:
      self.write("(")
      self.dispatch(t.left)
      self.write(" " + self.binop[name] + " ")
      self.dispatch(t.right)
      self.write(")")

  cmpops = {
    "Eq":"==",
    "NotEq":"!=",
    "Lt":"<",
    "LtE":"<=",
    "Gt":">",
    "GtE":">=",
    "Is":"===",
    "IsNot":"!==",
  }
  def _Compare(self, t):
    name = t.ops[0].__class__.__name__
    self.write("(")
    if name == 'In':
      comparator = t.comparators.pop()
      self.write('in_array(')
      self.dispatch(t.left)
      self.write(', ')
      self.dispatch(comparator)
      self.write(') || array_key_exists(')
      self.dispatch(t.left)
      self.write(', ')
      self.dispatch(comparator)
      self.write(')')
    elif name == 'NotIn':
      comparator = t.comparators.pop()
      self.write('!in_array(')
      self.dispatch(t.left)
      self.write(', ')
      self.dispatch(comparator)
      self.write(') && !array_key_exists(')
      self.dispatch(t.left)
      self.write(', ')
      self.dispatch(comparator)
      self.write(')')
    else:
      self.dispatch(t.left)
      for o, e in zip(t.ops, t.comparators):
        self.write(" " + self.cmpops[o.__class__.__name__] + " ")
        self.dispatch(e)
    self.write(")")

  boolops = {ast.And: '&&', ast.Or: '||'}
  def _BoolOp(self, t):
    self.write("(")
    s = " %s " % self.boolops[t.op.__class__]
    interleave(lambda: self.write(s), self.dispatch, t.values)
    self.write(")")

  def _Attribute(self,t):
    self.dispatch(t.value)
    self.write("->")
    self.write(t.attr)

  def _func_name(self, t):
    self.write('%s' % t.id)

  def _Call(self, t):
    self._func_name(t.func)
    self.write("(")
    comma = False
    for e in t.args:
      if comma: self.write(", ")
      else: comma = True
      self.dispatch(e)
    for e in t.keywords:
      if comma: self.write(", ")
      else: comma = True
      self.dispatch(e)
    if t.starargs:
      self.error('function vararg not supported')
    if t.kwargs:
      self.error('function kwarg not supported')
    self.write(")")

  def _Subscript(self, t):
    if isinstance(t.slice, ast.Index):
      #self.dispatch(t.value)
      #self.write("[")
      #self.dispatch(t.slice)
      #self.write("]")
      self.write('pyphp_subscript(')
      self.dispatch(t.value)
      self.write(', ')
      self.dispatch(t.slice)
      self.write(')')
    elif isinstance(t.slice, ast.Slice):
      self.write('array_slice(')
      self.dispatch(t.value)
      self.write(', ')
      self.dispatch(t.slice)
      self.write(')')

  def _Ellipsis(self, t):
    self.error('ellipsis not supported')

  def _Index(self, t):
    self.dispatch(t.value)

  def _Slice(self, t):
    if t.lower:
      self.dispatch(t.lower)
    else:
      self.write('0')
    if t.upper:
      self.write(", ")
      self.write('(')
      self.dispatch(t.upper)
      self.write(' - ')
      if t.lower:
        self.dispatch(t.lower)
      else:
        self.write('0')
      self.write(')')
    if t.step:
      self.error('slice step not supported')

  def _ExtSlice(self, t):
    self.error('extslice not supported')
    #interleave(lambda: self.write(', '), self.dispatch, t.dims)

  ### Others ###

  def _arguments(self, t):
    first = True
    defaults = [None] * (len(t.args) - len(t.defaults)) + t.defaults
    for a,d in zip(t.args, defaults):
      if first: first = False
      else: self.write(", ")
      self.dispatch(a),
      if d:
        self.write(" = ")
        self.dispatch(d)
    if t.vararg:
      self.error('function vararg not supported')
    if t.kwarg:
      self.error('function kwarg not supported')

  def _keyword(self, t):
    self.write('$%s' % t.arg)
    self.write(" = ")
    self.dispatch(t.value)

  def _Lambda(self, t):
    self.write("(")
    self.write("function(")
    self.dispatch(t.args)
    self.write(") {")
    self.dispatch(t.body)
    self.write("})")

  def _alias(self, t):
    self.error('alias not supported')
