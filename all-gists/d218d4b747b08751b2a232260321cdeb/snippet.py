import types

# Helpers
# =======
def _obj():
  '''Dummy object'''
  return lambda: None

_FILLER = _obj()


# API
# ===
def Y(g):
  '''Y combinator - makes recursive lambdas
  ex: Y(lambda fact:
          lambda n:
            1 if n < 2 else n * fact(n - 1))(5)
  gives: 120
  '''
  exp = lambda f: g(lambda arg: f(f)(arg))
  return (exp)(exp)


def COND(cond_body_pairs, _else=lambda: None):
  '''Functional if-elif-...-else expression
  ex: COND((1==0, lambda: 'a',
            2==0, lambda: 'b',
            3==0, lambda: 'c'),
           _else= lambda: 'd')
  gives: 'd'

  Note: All conditions are evaluated immediately!
  For conditions that should be evaluated only
  when required, use IF.
  '''
  if len(cond_body_pairs) == 0:
    return _else()

  cond, body = cond_body_pairs[:2]
  if cond:
    return body()
  else:
    return COND(cond_body_pairs[2:], _else)


def IF(cond, then, _else=lambda: None):
  '''Functional if-then-else expression
  ex: IF(1==0, lambda: 'a',
         _else= lambda: 'b')
  gives: 'b'
  '''
  return COND((cond, then), _else)


def LET(bindings, body, env=None):
  '''Introduce local bindings.
  ex: LET(('a', 1,
           'b', 2),
          lambda o: [o.a, o.b])
  gives: [1, 2]

  Bindings down the chain can depend on
  the ones above them through a lambda.
  ex: LET(('a', 1,
           'b', lambda o: o.a + 1),
          lambda o: o.b)
  gives: 2
  '''
  if len(bindings) == 0:
    return body(env)

  env = env or _obj()
  k, v = bindings[:2]
  if isinstance(v, types.FunctionType):
    v = v(env)

  setattr(env, k, v)
  return LET(bindings[2:], body, env)


def FOR(bindings, body, env=None):
  '''Clojure style List comprehension.
  ex: FOR(('a', range(2),
           'b', range(2)),
          lambda o: (o.a, o.b))
  gives: [(0, 0), (0, 1), (1, 0), (1, 1)]

  Bindings down the chain can depend on
  the ones above them through a lambda
  like in LET.

  Special bindings take lambdas as values
  and can be used any number of times:
    * ':LET' - Temporary bindings
    * ':IF' - don't produce a value if this
      returns a falsey value
    * ':WHILE' - break out of the innermost
      loop if this returns a falsey value
  '''
  if len(bindings) == 0:
    tmp = body(env)
    return [] if tmp is _FILLER else [tmp]

  env = env or _obj()
  k, v = bindings[:2]
  if k == ':IF':
    cond = v(env)
    return FOR(bindings[2:],
               lambda e: body(e) if cond else _FILLER,
               env)
  elif k == ':LET':
    return LET(v,
               lambda e: FOR(bindings[2:], body, e),
               env)
  elif k == ':WHILE':
    if v(env):
      return FOR(bindings[2:], body, env)
    else:
      return []
  elif isinstance(v, types.FunctionType):
    v = v(env)

  res = []
  for x in v:
    setattr(env, k, x)
    res += FOR(bindings[2:], body, env)
    delattr(env, k)

  return res


# Tests
# =====
## LET form
assert LET(('a', 2,
            'b', lambda o: o.a * 3),
           lambda o: o.b - 1) == 5

## Y combinator (recursive lambda) and IF form
assert Y(lambda fact:
           lambda n:
             IF(n < 2, lambda: 1,
                _else= lambda: n * fact(n - 1)))(5) == 120

## FOR comprehension
assert FOR(('a', range(3)),
           lambda o: o.a + 1) == [1, 2, 3]

## Chained FOR comprehension
assert FOR(('a', range(3),
            ':IF', lambda o: o.a > 0,
            'b', lambda o: range(3 - o.a),
            ':LET', ('res', lambda o: [o.a, o.b]),
            ':WHILE', lambda o: o.a < 2),
           lambda o: o.res) == [
                                # filtered a == 0
                                [1, 0], [1, 1],
                                # stopped at a == 2
                               ]