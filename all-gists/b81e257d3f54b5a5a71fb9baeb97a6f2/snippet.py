import inspect
import ast
from textwrap import dedent

import tensorflow as tf

def escape_op_name(name):
  """
  It has to match with "^[A-Za-z0-9.][A-Za-z0-9_.\\-/]*$"
  """
  name = list(name)
  if name[0] == '_':
    name[0] = '.'
  return ''.join(name)

def vclass(cls):
  """
  this class decorator is able to write an scope that includes 
  the name of the class.
  This is not possible with tfscope because the class is not
  created when the decorator is called.
  """
  # return cls
  for name, method in inspect.getmembers(
    cls, lambda x: inspect.ismethod(x)):

    setattr(cls, name, 
        vfun(method, classname=cls.__name__))
  return cls

def vfun(fn, classname=None):
  source = dedent(inspect.getsource(fn))
  _ast = ast.parse(source)
  Transformer().visit(_ast)
  ast.fix_missing_locations(_ast)
  compiled = compile(
    _ast, filename="<string>", mode="exec")

  d = dict(locals(), **fn.__globals__)
  exec(compiled, d, d)


  if classname:
    name = classname + '.' + fn.__name__
  else:
    name =  fn.__name__

  def decorated(*args, **kwargs):
    with tf.name_scope(escape_op_name(name)):
      return fn(*args, **kwargs)

  return decorated

class Transformer(ast.NodeTransformer):
  def __init__(self):
    self.src = ""

  def translate(self, node):
    self.visit(node)
    return node

  def visit_Assign(self, node):
    try:
      if (len(node.targets) == 1 
        and type(node.targets[0]) is ast.Name):

        var_name = node.targets[0].id

        func_name =  self.func_with_modules(node.value.func)
        if self.accepts_name(func_name):
          for kw in node.value.keywords:
            if kw.arg == 'name':
              break
          else:
            node.value.keywords.append(
              ast.keyword(
                arg='name',
                value=ast.Str(s=var_name)))
    except:
      pass

    self.generic_visit(node)
    return node

  def func_with_modules(self, node):
    parts = []
    while(hasattr(node, 'value')):
      parts.append(node.attr)
      node = node.value
    parts.append(node.id)
    return '.'.join(reversed(parts))

  def accepts_name(self, name):
    obj = eval(name)
    if type(obj) is type:
      func = obj.__init__
    else:
      func = obj

    return 'name' in inspect.getargspec(func).args:
  
  def visit_FunctionDef(self, node):
    node.decorator_list = []
    self.generic_visit(node)
    return node